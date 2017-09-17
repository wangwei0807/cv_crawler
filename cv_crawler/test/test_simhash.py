
from cv_crawler.utils.simhash import SimhashGenerator

if __name__ == '__main__':
    s = 'asasassssssssssssssssssssddddddddddddddddddddaafasfa'
    sim = SimhashGenerator(s)
    sim1 = SimhashGenerator('asasassssssssssssssssssssddddddddddddddddddddaafasfa123')
    print(sim.distance(sim1))