# worker/enqueue.py
import argparse, os, json, redis
from rq import Queue

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--redis", default="redis://doctorvit-redis:6379/0")
    p.add_argument("--queue", default="doctorvit:queue")
    p.add_argument("--prompt", required=True)
    p.add_argument("--max_new_tokens", type=int, default=200)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--top_p", type=float, default=1.0)
    p.add_argument("--do_sample", action="store_true")
    args = p.parse_args()

    conn = redis.from_url(args.redis)
    q = Queue(args.queue, connection=conn)
    payload = {
        "prompt": args.prompt,
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "do_sample": args.do_sample
    }
    # The worker loads job_runner from worker.worker:job_runner
    job = q.enqueue("worker.worker.job_runner", payload)
    print(job.id)

if __name__ == "__main__":
    main()
