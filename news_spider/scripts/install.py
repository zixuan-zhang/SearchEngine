import sys
import os

PYH_FILE = 'news_spider.pth'

if __name__ == '__main__':
    paths = [path for path in sys.path if path.endswith('dist-packages')]
    if len(paths) > 0:
        dist_path = paths[0]
        pth_path = os.path.join(dist_path, PYH_FILE)
        if os.path.exists(pth_path):
            os.remove(pth_path)
        if not os.path.exists(PYH_FILE):
            with open(PYH_FILE, "w+") as fp:
                fp.write(os.getcwd())
        print 'Modifying python path...'
        os.link(PYH_FILE, pth_path)
