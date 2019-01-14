import sys
template = open(sys.argv[1]).read()
widgets  = open(sys.argv[2]).read()
sys.stdout.write(template.replace("\n### INSERT GENERATED GUI CLASSES HERE ###\n", "\n"+widgets))
