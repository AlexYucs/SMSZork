import os
import stat
import sys
import queue
from subprocess import PIPE, Popen
import threading

class Wrapper():
    def __init__(self):
        st = os.stat('./tools/dfrotz')
        os.chmod('./tools/dfrotz', st.st_mode | stat.S_IEXEC)
        try:
            self.frotz = Popen(
                './stories/zork.z5',
                executable = './tools/dfrotz',
                shell=True,
                stdin=PIPE,
                stdout=PIPE,
                bufsize=1
            )
        except OSError as e:
            print('OS error')
            sys.exit(0)
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.enqueue, args=(self.frotz.stdout, self.queue))
        self.thread.daemon = True
        self.thread.start()

    def send(self, command):
        print(command)
        #.encode('cp1252'))
        try:
            self.frotz.stdin.write((command).encode('utf-8'))
            self.frotz.stdin.flush()
        except IOError as e:
            print(e)
            debug_string = '[DEV] Pipe is broken. Please tell @mrtnb what you did.'
            return debug_string
    def enqueue(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()


    def generate_output(self):
        self.raw_output = ''.join(self.lines)

        # clean up Frotz' output
        self.output = self.raw_output.replace('> > ', '')
        self.output = self.output.replace('\n.\n', '\n\n')

        return self.output

    def get(self):
        self.lines = []
        while True:
            try:
                self.line = self.queue.get(timeout=1).decode('cp1252')
                self.line = '\n'.join(' '.join(line_.split()) for line_ in self.line.split('\n'))
            except queue.Empty:
                print('EMPTY QUEUE')
                break
            else:
                self.lines.append(self.line)

        for index, line in enumerate(self.lines):
            # long line (> 70 chars) could be a part of
            # a text passage - removing \n there to
            # make output more readable
            if len(line) >= 70 and line.endswith('\n'):
                self.lines[index] = line.replace('\n', ' ')

        return self.generate_output()

def main():
    wrap = Wrapper()
    while True:
        print(wrap.get())
        cmd = '%s\r\n' % input()
        wrap.send(cmd)
