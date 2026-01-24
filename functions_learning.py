def dblogger(msg):
    print(msg)

def main(logger):
    # do stuff
    logger("hello world")

main(dblogger)