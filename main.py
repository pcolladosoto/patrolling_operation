import query_foto as img, movement_script as m, threading, Queue, signal

def handler(a, b):
    exit()

def main():
    q, s_q = Queue.Queue(), Queue.Queue()

    signal.signal(signal.SIGINT, handler)

    thread_a = threading.Thread(target = m.movement, args = (s_q,))
    thread_a.daemon = True

    thread_b = threading.Thread(target = img.get_photo, args = (q,))
    thread_b.daemon = True

    thread_a.start()
    thread_b.start()

    while True:
        while not q.empty():
            if q.get() == "Stop!":
                print "Got STOP!"
                s_q.put("Stop!")

if __name__ == "__main__":
    main()
