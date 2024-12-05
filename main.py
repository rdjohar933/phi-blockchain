import node_5001
import node_5002
import node_5003
import multiprocessing

if __name__ == '__main__':
    t1 = multiprocessing.Process(target= node_5001.main_run)
    t2 = multiprocessing.Process(target= node_5002.main_run)
    t3 = multiprocessing.Process(target= node_5003.main_run)
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()