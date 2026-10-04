#!/usr/bin/env python
"""OpenHands V1 SDK headless runner for benchmark.
Usage: oh_run.py --task-dir DIR --prompt-file FILE --max-iterations N
Writes stdout events to DIR/agent_events.jsonl and final message to DIR/agent_output.txt
"""
import argparse, json, os, sys, time, datetime

p = argparse.ArgumentParser()
p.add_argument("--task-dir", required=True)
p.add_argument("--prompt-file", required=True)
p.add_argument("--prompt-file2", default=None, help="second turn prompt (same conversation — memory retention)")
p.add_argument("--max-iterations", type=int, default=40)
args = p.parse_args()

os.chdir(args.task_dir)
os.environ.setdefault("OPENHANDS_SUPPRESS_BANNER", "1")
prompt = open(args.prompt_file).read()

t0 = time.time()
meta = {"agent": "openhands", "version": "1.11.0 (sdk 1.34.0)", "started": datetime.datetime.now().isoformat()}
events_f = open(os.path.join(args.task_dir, "agent_events.jsonl"), "w")
def log_ev(obj):
    events_f.write(json.dumps(obj, default=str) + "\n"); events_f.flush()

from openhands.sdk import LLM, Agent, Conversation, Workspace, Message, TextContent
from openhands.sdk.event import AgentErrorEvent, MessageEvent, ActionEvent, ObservationEvent
from openhands.tools.preset.default import get_default_tools

api_key = os.environ["AGNES_API_KEY"]
base_url = os.environ["AGNES_BASE_URL"]
llm = LLM(model="openai/agnes-3.0-flash", base_url=base_url, api_key=api_key,
          usage_id="bench-oh", temperature=0.0, num_retries=6, retry_min_wait=2, retry_max_wait=30,
          timeout=600, max_output_tokens=8192)
tools = get_default_tools(enable_browser=False)
agent = Agent(llm=llm, tools=tools, max_iterations=args.max_iterations)
ws = Workspace(working_dir=args.task_dir)

def callback(ev):
    try:
        if isinstance(ev, ActionEvent):
            detail = json.dumps({"tool": type(ev.action).__name__,
                                 "params": str(getattr(ev.action, "parsed_args", getattr(ev.action, "args", "")))[:600]})
        else:
            detail = str(getattr(ev, "llm_message", "") or ev)[:1200]
        log_ev({"type": type(ev).__name__, "t": round(time.time()-t0,2), "detail": detail})
    except Exception:
        pass

conv = Conversation(agent=agent, workspace=ws, callbacks=[callback], max_iteration_per_run=args.max_iterations)

final = {"text": None}
def on_message(ev):
    if isinstance(ev, MessageEvent) and ev.role == "assistant" and ev.content:
        txt = "\n".join(c.text for c in ev.content if isinstance(c, TextContent))
        if txt.strip(): final["text"] = txt

try:
    conv.send_message(Message(role="user", content=[TextContent(text=prompt)]))
    conv.run()
    meta["status"] = str(getattr(conv.state, "execution_status", "unknown"))
    if args.prompt_file2:
        p2 = open(args.prompt_file2).read()
        final["text"] = None
        meta["turn2_started"] = datetime.datetime.now().isoformat()
        conv.send_message(Message(role="user", content=[TextContent(text=p2)]))
        conv.run()
        meta["status"] = str(getattr(conv.state, "execution_status", "unknown"))
except Exception as e:
    meta["status"] = "error"
    meta["error"] = str(e)[:2000]
    log_ev({"type": "RUNTIME_ERROR", "error": str(e)[:2000]})

dur = round(time.time()-t0, 1)
meta["duration_s"] = dur
meta["conversation_id"] = str(getattr(conv, "id", ""))
try:
    stats = conv.state.stats
    meta["tokens"] = {"input": stats.costs_by_usage and sum(c.prompt_tokens for c in stats.costs_by_usage.values()) or 0,
                      "output": stats.costs_by_usage and sum(c.completion_tokens for c in stats.costs_by_usage.values()) or 0}
except Exception: pass

events_f.close()
with open(os.path.join(args.task_dir, "agent_output.txt"), "w") as f:
    f.write(final["text"] or "[no final assistant message captured]")
with open(os.path.join(args.task_dir, "agent_meta.json"), "w") as f:
    json.dump(meta, f, indent=2)
print(json.dumps(meta))
sys.exit(0 if meta.get("status") in ("finished","idle","completed") and "error" not in meta else 3)
