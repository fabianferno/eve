"""Upload a local file to the MicroPython filesystem. Usage: upload.py PORT LOCAL REMOTE"""
import subprocess, sys, os, tempfile

port, local, remote = sys.argv[1:4]
data = open(local, "rb").read()
code = "f=open(%r,'wb')\n" % remote
for i in range(0, len(data), 512):
    code += "f.write(%r)\n" % data[i:i + 512]
code += "f.close()\nimport os\nprint(%r, os.stat(%r)[6], 'bytes')\n" % (remote, remote)
with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as t:
    t.write(code)
here = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, "-I", os.path.join(here, "mpexec.py"), port, t.name, "30"], check=True)
os.unlink(t.name)
