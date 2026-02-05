import asyncio
import logging
import os
from typing import Optional, List, Dict, Any

from backend.Sql.FCMClient import FCMClient
from backend.Sql.SClient import SupabaseClient
from common.env import load_env


logger = logging.getLogger(__name__)


class ChangeLogNotifier:
    def __init__(
        self,
        sb: SupabaseClient,
        fcm: FCMClient,
        topic: str = "sync",
        poll_interval: float = 1.0,
        batch_size: int = 200,
        start_from_latest: bool = True,
    ):
        self.sb = sb
        self.fcm = fcm
        self.topic = topic
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self.start_from_latest = start_from_latest
        self._last_version: Optional[int] = None
        self._stop = False

    def stop(self) -> None:
        self._stop = True

    def _get_latest_version(self) -> int:
        row = (
            self.sb._client
            .table("change_version")
            .select("version")
            .eq("id", 1)
            .single()
            .execute()
        ).data or {}
        return int(row.get("version", 0))

    def _fetch_changes(self, since: int) -> List[Dict[str, Any]]:
        return (
            self.sb._client
            .table("change_log")
            .select("entity_type, entity_id, change_type, version")
            .gt("version", since)
            .order("version", desc=False)
            .limit(self.batch_size)
            .execute()
        ).data or []

    async def _send_change(self, change: Dict[str, Any]) -> None:
        payload = {
            "type": "sync",
            "version": str(change.get("version", "")),
            "entity_type": str(change.get("entity_type", "")),
            "entity_id": str(change.get("entity_id", "")),
            "change_type": str(change.get("change_type", "")),
        }
        msg_id = await asyncio.to_thread(self.fcm.send_topic, self.topic, data=payload)
        logger.info("fcm sent topic=%s msg_id=%s payload=%s", self.topic, msg_id, payload)

    async def run(self) -> None:
        load_env()
        if self._last_version is None:
            self._last_version = self._get_latest_version() if self.start_from_latest else 0

        while not self._stop:
            try:
                changes = self._fetch_changes(self._last_version)
                if not changes:
                    await asyncio.sleep(self.poll_interval)
                    continue

                for change in changes:
                    try:
                        await self._send_change(change)
                    except Exception as exc:
                        logger.exception("send_topic failed: %s", exc)
                        await asyncio.sleep(self.poll_interval)
                        break
                    else:
                        try:
                            self._last_version = max(
                                self._last_version or 0,
                                int(change.get("version", 0)),
                            )
                        except Exception:
                            self._last_version = self._last_version or 0
            except Exception as exc:
                logger.exception("change_log polling failed: %s", exc)
                await asyncio.sleep(self.poll_interval)
