#test apis
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from torch.nn.utils.rnn import pack_padded_sequence
from dreamcoder.program import Hole
from dreamcoder.grammar import *
from dreamcoder.zipper import *
import random

def binary_cross_entropy(y,t, epsilon=10**-10, average=True):
    """y: tensor of size B, elements <= 0. each element is a log probability.
    t: tensor of size B, elements in [0,1]. intended target.
    returns: 1/B * - \sum_b t*y + (1 - t)*(log(1 - e^y + epsilon))"""

    B = y.size(0)
    log_yes_probability = y
    log_no_probability = torch.log(1 - y.exp() + epsilon)
    assert torch.ByteTensor.all(log_yes_probability <= 0.)
    assert torch.ByteTensor.all(log_no_probability <= 0.)
    correctYes = t
    correctNo = 1 - t
    ce = -(correctYes*log_yes_probability + correctNo*log_no_probability).sum()
    if average: ce = ce/B
    return ce


def sketchesFromProgram(e, tp, g):
    singleHoleSks = list( sk for sk, _ in g.enumerateHoles(tp, e, k=10))
    """
    really bad code for getting two holes
    """
    sketches = []
    for expr in singleHoleSks:
        for sk, _ in g.enumerateHoles(tp, expr, k=10):
            sketches.append(sk)
    return sketches 

def negSketchFromProgram(e, tp, g):
    # TODO
    assert 0
    for mut in g.enumerateNearby(request, expr, distance=3.0): #Need to rewrite
        g.enumerateHoles(self, request, expr, k=10, return_obj=Hole)
        pass

def stringify(line):
    lst = []
    string = ""       
    for char in line+" ": 
        if char == " ":  
            if string != "":      
                lst.append(string)     
            string = ""              
        elif char in '()':            
            if string != "":        
                lst.append(string)     
            string = ""                
            lst.append(char)        
        else:                       
            string += char       
    return lst


class BaseValueHead(nn.Module):
    def __init__(self):
        super(BaseValueHead, self).__init__()

    def computeValue(self, sketch, task):
        assert False, "not implemented"

    # def computeValueLoss(task, positiveSketch, negativeSketch):
    #     assert False, "not implemented"

    def valueLossFromFrontier(frontier, g):
        assert False, "not implemented"

class SimpleRNNValueHead(BaseValueHead):

    def __init__(self, g, featureExtractor, H=512):
        #specEncoder can be None, meaning you dont use the spec at all to encode objects
        super(SimpleRNNValueHead, self).__init__()
        self.use_cuda = torch.cuda.is_available() #FIX THIS

        extras = ['(', ')', 'lambda', '<HOLE>', '#'] + ['$'+str(i) for i in range(10)] 

        self.lexicon = [str(p) for p in g.primitives] + extras
        self.embedding = nn.Embedding(len(self.lexicon), H)

        self.wordToIndex = {w: j for j,w in enumerate(self.lexicon) }

        self.model = nn.GRU(H,H,1)
        self.H = H
        self.outputDimensionality = H

        self._distance = nn.Sequential(
                nn.Linear(featureExtractor.outputDimensionality + H, H),
                nn.ReLU(),
                nn.Linear(H, 1),
                nn.Softplus())

        self.featureExtractor = featureExtractor

        if self.use_cuda:
            self.cuda()

    def _encodeSketches(self, sketches):
        #don't use spec, just there for the API
        assert type(sketches) == list

        #idk if obj is a list of objs... presuably it ususaly is 
        tokens_list = [ stringify(str(sketch)) for sketch in sketches]

        symbolSequence_list = [[self.wordToIndex[t] for t in tokens] for tokens in tokens_list]

        inputSequences = [torch.tensor(ss) for ss in symbolSequence_list] #this is impossible

        if self.use_cuda: #TODO
            inputSequences = [s.cuda() for s in inputSequences]

        inputSequences = [self.embedding(ss) for ss in inputSequences]

        # import pdb; pdb.set_trace()
        idxs, inputSequence = zip(*sorted(enumerate(inputSequences), key=lambda x: -len(x[1])  ) )
        try:
            packed_inputSequence = torch.nn.utils.rnn.pack_sequence(inputSequence)
        except ValueError:
            print("padding issues, not in correct order")
            import pdb; pdb.set_trace()

        _,h = self.model(packed_inputSequence) #dims
        unperm_idx, _ = zip(*sorted(enumerate(idxs), key = lambda x: x[1]))
        h = h[:, unperm_idx, :]
        h = h.squeeze(0)
        #o = o.squeeze(1)

        objectEncodings = h
        return objectEncodings

    def computeValue(self, sketch, task):
        taskFeatures = self.featureExtractor.featuresOfTask(task).unsqueeze(0) #memoize this plz
        sketchEncoding = self._encodeSketches([sketch])
        
        return self._distance(torch.cat([sketchEncoding, taskFeatures], dim=1)).squeeze(1).data.item()

    def valueLossFromFrontier(self, frontier, g):
        """
        given a frontier, should sample a postive trace and a negative trace
        and then train value head on those
        """
        #TODO


        features = self.featureExtractor.featuresOfTask(frontier.task)
        if features is None: return None, None
        features = features.unsqueeze(0)

        # Monte Carlo estimate: draw a sample from the frontier
        entry = frontier.sample()
        tp = frontier.task.request
        fullProg = entry.program._fullProg
        posTrace, negTrace =  getTracesFromProg(fullProg, frontier.task.request, g)

        #discard negative sketches which overlap with positive
        negTrace = [sk for sk in negTrace if (sk not in posTrace) ]

        nPos = len(posTrace)
        nNeg = len(negTrace)
        nTot = nPos + nNeg

        sketchEncodings = self._encodeSketches(posTrace + negTrace)
        #import pdb; pdb.set_trace()

        # copy features a bunch
        distance = self._distance(torch.cat([sketchEncodings, features.expand(nTot, -1)], dim=1)).squeeze(1)

        targets = [1.0]*nPos + [0.0]*nNeg
        targets = torch.tensor(targets)
        if self.use_cuda:
            targets = targets.cuda()

        loss = binary_cross_entropy(-distance, targets, average=False) #average?
        return loss


class AbstractREPLValueHead(BaseValueHead):

    def __init__(dsl):
        pass 

        #call the thing which converts 

    def computeValue(self, sketch, task):
        pass

        sketch = self._convertSketch(sketch)

    def _convertSketch(self, sketch):
        pass

    def abstractREPL(self, sketch, task):
        pass 

    def trainAbstractREPL():
        pass



"""
object for 

make a value head object
you can have different types of valueHeads
the api is:


def computeValue(self, sketch, task)

def computeLoss(self, posSketch, negSketch, task):
"""

if __name__ == '__main__':
    try:
        import binutil  # required to import from dreamcoder modules
    except ModuleNotFoundError:
        import bin.binutil  # alt import if called as module


    from dreamcoder.domains.arithmetic.arithmeticPrimitives import *
    g = ContextualGrammar.fromGrammar(Grammar.uniform([k0,k1,addition, subtraction]))
    g = g.randomWeights(lambda *a: random.random())
    #p = Program.parse("(lambda (+ 1 $0))")

    m = RNNSketchEncoder(g)

    request = arrow(tint,tint)
    for ll,_,p in g.enumeration(Context.EMPTY,[],request,
                               12.):
        ll_ = g.logLikelihood(request,p)
        print(ll,p,ll_)
        d = abs(ll - ll_)
        assert d < 0.0001

        encoding = m([p])

        assert 0



