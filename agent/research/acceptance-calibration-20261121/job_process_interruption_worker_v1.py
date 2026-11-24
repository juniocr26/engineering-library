"""Owned abrupt-exit worker; no source/helper/model execution or production edit."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
ROOT = P.parents[2]
protocol = json.loads((P / 'job-process-interruption-protocol-v1.json').read_text())
for item in protocol['source_files']:
    assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
sys.path.insert(0, str(ROOT / 'agent/tools'))
import documentation_workspace as workspace
import documentation_job_budget as jobs

phase = sys.argv[1]
folder = Path(sys.argv[2]).resolve()
assert folder.is_relative_to(P / 'job-process-interruption-v1')
stage = 'config'
original_write = os.write


def interrupted_write(descriptor, data):
    if phase == 'mid_' + stage:
        body = bytes(data)
        # There is no buffered IO or cleanup: publish an actual partial file,
        # then stop only this controlled worker process.
        assert len(body) > 4
        original_write(descriptor, body[:len(body) // 2])
        os._exit(91)
    return original_write(descriptor, data)


os.write = interrupted_write
clock = lambda: datetime.datetime.fromisoformat(protocol['clock'])
budget = jobs.HelperJobBudget(folder / 'job-journal', protocol['config'], clock=clock)
if phase == 'after_config':
    os._exit(91)
stage = 'reservation'
ticket = budget.reserve(protocol['request'])
assert ticket['status'] == 'RESERVED', ticket
if phase == 'after_reservation':
    os._exit(91)
stage = 'delivery'
body = jobs.canonical(protocol['body'])
with workspace.directory(folder / 'delivery') as descriptor:
    workspace.write_new(descriptor, 'body.json', body)
if phase == 'after_delivery':
    os._exit(91)
stage = 'completion'
completion = budget.complete(ticket, protocol['body'])
assert completion['status'] == 'COMPLETED', completion
if phase == 'after_completion':
    os._exit(91)
raise RuntimeError('Unknown phase; no unplanned successful worker exit')
