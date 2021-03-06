#!/usr/bin/env python2

# Based on BIP39
# https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki

from time import time
from random import shuffle, choice
import sys

def hamming(ww,w):
    '''
    find the hamming distance between words w and u
    '''

    l = []
    if len(w) > len(ww):
        ww,w = w,ww
        # ww is the longest

    for o in range(len(ww) - len(w) + 1):
        d = 0
        for h,k in zip(ww,' '*o + w):
            if h != k:
                d += 1
        d += len(ww) - (len(w)+o)
        l.append(d)
    return min(l)


is_alpha = lambda w: not bool([c for c in w if c<'a' or c>'z'])
is_not_the_same_letter = lambda w: w.strip(w[0])

def load_words(fname):
    
    with open(fname) as f:
        return [x.strip() for x in f.readlines() if len(x.strip())>=3 and is_alpha(x.strip()) and is_not_the_same_letter(x.strip())]

def hamming_table(www):

    table = {}
    for i in range(len(www)):
        #print 'Word:',www[i]
        for j in range(i+1,len(www)):

            # change: do the check, since m'in not interest only in .4 file
            #if www[i][:4] == www[j][:4]:
                # One of those two words can't be selected, i'll not compere them
            #    continue

            h = hamming(www[i],www[j])
            value = table.get(h,[])
            value.append( (i,j) )
            table[h] = value
    return table

def remove_similars(www,min_valid_h):

    i = 0
    t =time()
    while i<len(www):
        if i%100==0 and i and time()-t>10:
            print 'Word number: %d/%d time [s]: %.2f'%(i,len(www),time()-t)
            t = time()
        to_del = []
        for j in range(i+1,len(www)):
            if hamming(www[i],www[j]) < min_valid_h:
                to_del.append(j)
        # delete process is arbitrary... A better choice could be done
        for d in reversed(to_del):
            del www[d]
        i += 1
            
def fourgroup(www,four):

    table = {}
    for w in www:
        value = table.get(w[:four],[])
        value.append(w)
        table[w[:four]] = value

    return table.values()

def fourfilter(www,four):
    
    out = []
    for v in fourgroup(www,four):
        out.append(v[0])

    return out

def main():
    # test
    assert hamming("ciao","ciao") == 0
    assert hamming("ciao","cia") == 1
    assert hamming("mare","pare") == 1
    assert hamming("","pare") == 4
    assert hamming("re","pare") == 2
    assert hamming("ar","pare") == 2
    assert hamming("abcdefghi","d") == 8
    
    if len(sys.argv) < 6:
        print 'USAGE:'
        print './select.py <input-file> <min-hamming-distance>'
        print  '                         <ok> <ni> <blacklist>'
        sys.exit(1)
    
    fname = sys.argv[1]
    min_valid_h = int(sys.argv[2])
    
    ok = set(load_words(sys.argv[3]))
    ni = set(load_words(sys.argv[4]))
    blacklist = set(load_words(sys.argv[5]))

    www = list(ok) + \
          list(set(load_words(fname)) - ok - blacklist) + \
          list(ni)

    print 'fourfilter len:', len(fourfilter(www,4))

    #piece_dim = 25
    #parameters = (piece_dim,min_valid_h)
    parameters = ('rs',min_valid_h)

    tbegin = time()

    wwww = www[:]
    remove_similars(wwww,min_valid_h)

    four = fourfilter(wwww,4)
    ttot = (time()-tbegin) / 60.
    print '??',len(wwww),'time [m]: %.2f' % (ttot)

    print 'fourfilter len:', len(four)

    with open(fname+'-%s-%d' % parameters,'w') as f:
        f.writelines([x+'\n' for x in sorted(wwww)])

    with open(fname+'-%s-%d.4' % parameters,'w') as f:
        f.writelines([x+'\n' for x in sorted(four)])

    with open(fname+'-%s-%d.4.grouped' % parameters,'w') as f:
        f.writelines([' '+' '.join(x)+'\n' for x in 
                      sorted( 
                          mark(
                              mark(fourgroup(wwww,4),ok),
                              ni,lambda x: '!'+x),
                          lambda x,y: cmp(x[0].strip(' *!'),y[0].strip(' *!'))
                      )])

    print 'Output:',fname+'-%s-%d'% parameters

def mark(data,approved,
         marker=lambda x: '*'+x):

    out = []
    for line in data:
        out.append([marker(x) if x in approved else x for x in line])
    return out

if __name__=="__main__":
    main()
