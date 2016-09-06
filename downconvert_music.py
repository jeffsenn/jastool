import os,sys
EXTENSIONS=('mp3','m4a','aac','wav','aif','mp2')

def process_file(src,dst):
  print "FILE: ",src, dst
  if os.path.exists(dst):
      return 1
  dst = dst.split('.')
  dst[-1] = 'mp3'
  dst = '.'.join(dst)
  dst = "/tmp/foo.mp3"
  if os.path.exists(dst):
      return 2
  os.system("ffmpeg -i '%s' -b:a 128000 '%s'" %(src,dst))
  # compare sizes
  s1 = os.path.getsize(src)
  s2 = os.path.getsize(dst)
  ratio = s2 / s1
  print "SIZES",s1,s2,ratio
  if ratio < 0.90:
      print "Using orignal:",dst
      open(dst,"wb").write(open(src,"rb").read())
  else:
      print "Converted:",dst
  lkjdsf
  
def process_dir(src,dst):
  not_processed = {}
  for root, dirs, files in os.walk(src):
    for name in files:
      #print(os.path.join(root, name))
      x = name.split('.')
      if len(x) > 1:
          x = x[-1].lower()
          if x in EXTENSIONS:
            snm = os.path.join(root,name)
            dnm = dst+snm[len(src):]
            process_file(snm,dnm)
          elif x not in not_processed:
            not_processed[x] = None
            print x
        
    #for name in dirs:
    #    print(os.path.join(root, name))

if __name__ == "__main__":
    process_dir(sys.argv[1],".")
