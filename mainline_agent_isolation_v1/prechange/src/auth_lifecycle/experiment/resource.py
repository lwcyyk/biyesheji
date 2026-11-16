"""Controlled resource/broker fixture; explicitly NOT an authentication implementation."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
import secrets
import threading
import urllib.error
import urllib.request


class Resource:
    def __init__(self, witness, actor, mode, journal, query_client=0):
        self.witness=witness;self.actor=actor;self.mode=mode;self.journal=journal;self.query_client=query_client
        self.tokens={};self.closed=set();self.admin=secrets.token_urlsafe(32);self.lock=threading.Lock()
        owner=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def reply(self,status,payload):
                raw=json.dumps(payload).encode();self.send_response(status);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(raw)));self.end_headers();self.wfile.write(raw)
            def do_POST(self):
                if not hmac.compare_digest(self.headers.get("X-Lab-Control",""),owner.admin):self.reply(403,{});return
                task=self.path.removeprefix("/close/")
                if task not in owner.tokens:self.reply(404,{});return
                with owner.lock:owner.closed.add(task)
                owner.journal.emit("broker_gate_closed","resource",task=task)
                self.reply(200,{"closed":task})
            def do_GET(self):
                parts=self.path.strip("/").split("/")
                if len(parts)!=2 or parts[0] not in {"use","remote"} or parts[1] not in owner.tokens:self.reply(404,{});return
                route,task=parts;token=self.headers.get("Authorization","").removeprefix("Bearer ")
                if not hmac.compare_digest(token,owner.tokens[task]):self.reply(403,{});return
                if route=="use" and task in owner.closed:accepted=False
                else:
                    try:accepted=owner.witness.accepted(token,owner.mode,subject=owner.actor["id"],query_client=owner.query_client)
                    except Exception:accepted=None
                owner.journal.emit("resource_decision","resource",task=task,route=route,accepted=accepted,mode=owner.mode)
                self.reply(503 if accepted is None else 200 if accepted else 403,{"accepted":accepted})
        self.server=ThreadingHTTPServer(("127.0.0.1",0),Handler);self.thread=threading.Thread(target=lambda:self.server.serve_forever(poll_interval=.05),daemon=True);self.thread.start()
        self.url=f"http://127.0.0.1:{self.server.server_port}"

    def bind(self,mapping):self.tokens=dict(mapping)

    def request(self,path,token=None,close=False):
        headers={"X-Lab-Control":self.admin} if close else {"Authorization":"Bearer "+token}
        req=urllib.request.Request(self.url+path,data=b"" if close else None,headers=headers,method="POST" if close else "GET")
        try:r=urllib.request.urlopen(req,timeout=10)
        except urllib.error.HTTPError as e:r=e
        return {"http":r.status,"body":json.loads(r.read())}

    def close_task(self,task):return self.request("/close/"+task,close=True)
    def evaluate(self,task,remote=False):
        response=self.request(("/remote/" if remote else "/use/")+task,self.tokens[task])
        return response["body"].get("accepted") if response["http"] in {200,403} else None
    def shutdown(self):self.server.shutdown();self.server.server_close();self.thread.join()
