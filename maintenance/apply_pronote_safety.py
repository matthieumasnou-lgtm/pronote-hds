#!/usr/bin/env python3
"""Validated, idempotent local patch for Pronote HA 2.4.5.

Dry-run by default. --apply creates dated backups outside HACS-managed files.
Never run automatically on an unknown upstream release.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path('/homeassistant/custom_components/pronote')
BACKUPS = Path('/homeassistant/pronote_local_backups')
VERSION = '2.4.5'
MARKER = '# PRONOTE_LOCAL_SAFETY_2026_10_12'


def replace_once(src: str, before: str, after: str, name: str) -> str:
    count = src.count(before)
    if count != 1:
        raise ValueError(f'{name}: expected one match, found {count}')
    return src.replace(before, after, 1)


def patch_server(src: str) -> str:
    src = replace_once(src, 'PROBE_INTERVAL = timedelta(minutes=5)',
                       'PROBE_INTERVAL = timedelta(minutes=60)', 'server interval')
    src = replace_once(src, 'PROBE_TIMEOUT = 15\n', '''PROBE_TIMEOUT = 15

''' + MARKER + '''
# Entries for two children pointing at the same URL share one probe.
_PROBE_LOCKS: dict[str, asyncio.Lock] = {}
_PROBE_CACHE: dict[str, tuple] = {}
''', 'server cache')
    old = '''    async def _async_probe(self) -> None:
        """Probe the Pronote server and update the status state."""
        session = async_get_clientsession(self.hass)
        status: int | None = None
        try:
            async with session.get(
                self._base_url,
                timeout=aiohttp.ClientTimeout(total=PROBE_TIMEOUT),
                allow_redirects=True,
            ) as response:
                status = response.status
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.debug(
                "Pronote server status probe failed for %s: %s", self._base_url, err
            )
            status = None

        self._http_status = status
        self._attr_native_value = server_status_from_http(status)
        self._last_checked = dt_util.now().isoformat()
'''
    new = '''    async def _async_probe(self) -> None:
        """Probe at most once per hour for a shared Pronote URL."""
        lock = _PROBE_LOCKS.setdefault(self._base_url, asyncio.Lock())
        async with lock:
            now = dt_util.now()
            cached = _PROBE_CACHE.get(self._base_url)
            if cached and now - cached[0] < PROBE_INTERVAL:
                status, checked_at = cached[1], cached[2]
            else:
                session = async_get_clientsession(self.hass)
                status: int | None = None
                try:
                    async with session.get(
                        self._base_url,
                        timeout=aiohttp.ClientTimeout(total=PROBE_TIMEOUT),
                        allow_redirects=True,
                    ) as response:
                        status = response.status
                except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                    _LOGGER.debug("Pronote server probe failed for %s: %s", self._base_url, err)
                checked_at = dt_util.now().isoformat()
                _PROBE_CACHE[self._base_url] = (now, status, checked_at)
        self._http_status = status
        self._attr_native_value = server_status_from_http(status)
        self._last_checked = checked_at
'''
    return replace_once(src, old, new, 'shared HTTP probe')


def patch_auth(src: str) -> str:
    src = replace_once(src, 'import logging\nimport re\n', '''import logging
import re
import threading
import time
''', 'helper imports')
    src = replace_once(src, '_LOGGER = logging.getLogger(__name__)\n', '''_LOGGER = logging.getLogger(__name__)

''' + MARKER + '''
# One guarded login per shared parent account, with bounded exponential cooldown.
# In-memory only: never write credentials or access tokens to logs/disk.
_AUTH_LOCK = threading.Lock()
_AUTH_FAILURES: dict[tuple, int] = {}
_AUTH_RETRY_AFTER: dict[tuple, float] = {}
''', 'helper guard')
    before = '''def get_pronote_client(data) -> pronotepy.Client | pronotepy.ParentClient | None:
    _LOGGER.debug(f"Coordinator uses connection: {data['connection_type']}")

    if data["connection_type"] == "qrcode":
        client = get_client_from_qr_code(data)
    else:
        client = get_client_from_username_password(data)

    if client is None:
        _LOGGER.warning("Client creation failed")
        return None

    try:
        client.session_check()
    except Exception as e:
        _LOGGER.error("Session check failed: %s", e)

    return client
'''
    after = '''def get_pronote_client(data) -> pronotepy.Client | pronotepy.ParentClient | None:
    """Serialize matching parent logins and stop retry storms after failure."""
    # Group both child profiles, but keep distinct credentials separate.
    account = (data.get("url") or data.get("qr_code_url") or "",
               data.get("username") or data.get("qr_code_username") or "")
    with _AUTH_LOCK:
        now = time.monotonic()
        if now < _AUTH_RETRY_AFTER.get(account, 0):
            return None

        if data["connection_type"] == "qrcode":
            client = get_client_from_qr_code(data)
        else:
            client = get_client_from_username_password(data)

        if client is None:
            failures = _AUTH_FAILURES.get(account, 0) + 1
            _AUTH_FAILURES[account] = failures
            delay_seconds = min(2 * 3600 * (2 ** min(failures - 1, 3)), 12 * 3600)
            _AUTH_RETRY_AFTER[account] = time.monotonic() + delay_seconds
            _LOGGER.warning("Pronote login failed: suspending retries for %d minutes", delay_seconds // 60)
            return None

        _AUTH_FAILURES.pop(account, None)
        _AUTH_RETRY_AFTER.pop(account, None)
        try:
            client.session_check()
        except Exception as exc:
            # Keep upstream behavior: session_check errors can be non-fatal.
            _LOGGER.warning("Pronote session check failed: %s", type(exc).__name__)
        return client
'''
    return replace_once(src, before, after, 'login guard')


def patch_coordinator(src: str) -> str:
    src = replace_once(src, '        self.config_entry = entry\n', '''        self.config_entry = entry
''' + '        ' + MARKER + '''
        self._data_stale = False
        self._stale_keys: set[str] = set()
        self._last_live_refresh_at = None
        self._last_key_refresh: dict = {}
''', 'coordinator init')
    old = '''        client = await self.hass.async_add_executor_job(get_pronote_client, config_data)
        if client is None:
            _LOGGER.error("Unable to init pronote client")
            return None

        try:
            return await self._fetch_data(client, today, previous_data)
        finally:
'''
    new = '''        client = await self.hass.async_add_executor_job(get_pronote_client, config_data)
        if client is None:
            # Keep previously fetched data, do not emit false empty grades.
            self._data_stale = True
            self._stale_keys = set(previous_data or {})
            if previous_data is not None:
                self.data = previous_data
            return previous_data

        try:
            try:
                result = await self._fetch_data(client, today, previous_data)
                if result is None:
                    self._data_stale = True
                    self._stale_keys = set(previous_data or {})
                    if previous_data is not None:
                        self.data = previous_data
                    return previous_data
                self._data_stale = False
                self._last_live_refresh_at = datetime.now(ZoneInfo(self.hass.config.time_zone))
                for key, value in result.items():
                    if value is not None and key not in self._stale_keys:
                        self._last_key_refresh[key] = self._last_live_refresh_at
                return result
            except Exception as err:
                self._data_stale = True
                self._stale_keys = set(previous_data or {})
                _LOGGER.warning("Pronote update failed, last good data retained: %s", type(err).__name__)
                if previous_data is not None:
                    self.data = previous_data
                    return previous_data
                raise
        finally:
'''
    src = replace_once(src, old, new, 'coordinator failure fallback')
    old2 = '''        # Strip _client back-references to allow GC of the client object graph
'''
    new2 = '''        # Partial data failures must not erase previously valid grades.
        # Only reuse values from the SAME school period; flag staleness in HA.
        self._stale_keys = set()
        if previous_data and previous_data.get("current_period_key") == self.data.get("current_period_key"):
            for key in ("grades", "averages", "overall_average"):
                if self.data.get(key) is None and previous_data.get(key) is not None:
                    self.data[key] = previous_data[key]
                    self._stale_keys.add(key)

''' + old2
    return replace_once(src, old2, new2, 'partial grade fallback')


def patch_sensor(src: str) -> str:
    old = '''        if self.coordinator.data[self._coordinator_key] is None:
            return "unavailable"
'''
    src = replace_once(src, old, '''        if not self.coordinator.data or self.coordinator.data.get(self._coordinator_key) is None:
            return "unavailable"
''', 'sensor native data guard')
    old2 = '''            "updated_at": self.coordinator.last_update_success_time,
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
                self.coordinator.last_update_success
                and self.coordinator.data[self._coordinator_key] is not None
        )
'''
    new2 = '''            # PRONOTE_LOCAL_SAFETY_2026_10_12
            "updated_at": getattr(self.coordinator, "_last_key_refresh", {}).get(
                self._coordinator_key, self.coordinator.last_update_success_time
            ),
            "data_stale": bool(
                getattr(self.coordinator, "_data_stale", False)
                or self._coordinator_key in getattr(self.coordinator, "_stale_keys", set())
            ),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return bool(
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.coordinator.data.get(self._coordinator_key) is not None
        )
'''
    return replace_once(src, old2, new2, 'sensor staleness marker')


def patch_calendar(src: str) -> str:
    old='''        try:
            lessons = self.coordinator.data["lessons_period"]
            if lessons is None:
                return None

            now = datetime.now()
'''
    new='''        try:
            # PRONOTE_LOCAL_SAFETY_2026_10_12
            data = self.coordinator.data or {}
            lessons = data.get("lessons_period")
            if lessons is None:
                self._event = None
                super()._handle_coordinator_update()
                return

            now = datetime.now()
'''
    src=replace_once(src,old,new,'calendar coordinator None guard')
    src=replace_once(src,'''                self.coordinator.data["lessons_period"],
''','''                (self.coordinator.data or {}).get("lessons_period") or [],
''','calendar event list guard')
    return src


PATCHES = {
    'server_status.py': patch_server,
    'pronote_helper.py': patch_auth,
    'coordinator.py': patch_coordinator,
    'sensor.py': patch_sensor,
    'calendar.py': patch_calendar,
}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true',help='write after validation and backing up')
    parser.add_argument('--root',type=Path,default=ROOT)
    args=parser.parse_args()
    root=args.root
    manifest=json.loads((root/'manifest.json').read_text())
    if manifest.get('version') != VERSION:
        raise SystemExit(f"Unsupported Pronote version: {manifest.get('version')} (only {VERSION}); merge manually before upgrading")

    originals={}
    output={}
    for name, transform in PATCHES.items():
        path=root/name
        before=path.read_text(encoding='utf-8')
        originals[name]=before
        if MARKER in before:
            output[name]=before
            print(f'{name}: already patched')
            continue
        after=transform(before)
        ast.parse(after,filename=name)
        output[name]=after
        print(f'{name}: validated +{len(after)-len(before)} bytes')

    if not args.apply:
        print('Dry-run OK: no files modified')
        return
    suffix=datetime.now().strftime('%Y%m%d_%H%M%S')
    folder=BACKUPS/suffix
    folder.mkdir(parents=True,exist_ok=False)
    for name, before in originals.items():
        (folder/name).write_text(before,encoding='utf-8')
    (folder/'manifest.json').write_text((root/'manifest.json').read_text(),encoding='utf-8')
    (folder/'ROLLBACK.txt').write_text('Stop HA before restoring the saved files. Restore original files to custom_components/pronote and restart HA.\n')
    changed=[]
    try:
        for name, after in output.items():
            if after == originals[name]:
                continue
            path=root/name
            with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=root,delete=False,prefix=f'.{name}.') as f:
                f.write(after)
                tmp=Path(f.name)
            tmp.chmod(path.stat().st_mode)
            tmp.replace(path)
            changed.append(name)
        for name in PATCHES:
            ast.parse((root/name).read_text(encoding='utf-8'),filename=name)
    except Exception:
        for name in changed:
            (root/name).write_text(originals[name],encoding='utf-8')
        raise
    print('Applied:', ', '.join(changed) if changed else 'already applied')
    print('Backups:', folder)

if __name__=='__main__':
    main()
