import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
wnl = WordNetLemmatizer()

class ViterbiParser(object):
    def multi_dimensions(self, n):
        from collections import defaultdict
        """ Creates an n-dimension dictionary
        """  
        if n<=1:
          return dict
        return defaultdict(lambda:self.multi_dimensions(n-1))

    def __init__(self):
        self.ip_sentence = ""
        self.nt_list = []
        self.final_all_rules = []
        self.words = []
        self.root_word_variants = {}
        self.lex = self.multi_dimensions(3)
        self.syn = self.multi_dimensions(4)
        self.delta = self.multi_dimensions(4)
        self.chart = self.multi_dimensions(4)
        self.pOfW = []
        
    def printDict(self, dic):
        for keys,values in dic.items():
          print(keys)
          print(values)

    def read_input(self):
        import fileinput
        i = 0
        inp = ""
        inp_arr = []
        self.ip_sentence = ""
        expect_new_rule = True
        expect_all_input_done = False
        for line in fileinput.input():
            inp_arr.append(line)
            i +=1
            str_line = line.split("#")
            line = str_line[0].strip()
            if line == '':  # ignore comments
                continue
            if expect_all_input_done:
                print(("FATAL ERROR: erroroneous input. Expect sentence input at the end.", " Error Line number " , i))
                return None, None

            if expect_new_rule:
                if line.find("=") != -1:
                    self.ip_sentence = line
                    print("input sentence is:")
                    print(self.ip_sentence)
                    expect_all_input_done = True # input sentence is the last in the input
                else:
                    if not line[0].isalpha() or not line[0].isupper():
                        print(("FATAL ERROR: Rule does not start with a capitalized NT", " Error Line number " , i))
                        return None, None
                    if line.find("->") != -1:
                        print (("FATAL ERROR: Rule uses delimiter \"->\""    , " Error Line number " , i))
                        return None, None
                    if line.find(":") == -1:                
                        print (("FATAL ERROR: Rule uses delimiter other than \":\""    , " Error Line number " , i))
                        return None, None
                    if line.endswith(';'):
                        expect_new_rule = True
                    else:
                        expect_new_rule = False
                    inp += line
            else: # Looking for more parts of rule
                if not line.startswith('|'):
                    print (("FATAL ERROR: Previous rule likely not ended or missing | at start.", " Error Line number " , i))
                    return None, None
                if line.endswith(';'):
                    expect_new_rule = True
                inp += line
        #print("input is:")
        print(inp)
        return inp, inp_arr

    def get_all_rules_array_from_ip(self, inputStr):
        inputStr.strip()
        all_rules = inputStr.split(";")
        return all_rules 

    def breakdown_rhs(all_rhs_for_rule):
        #stripping is done earlier
        rhs_parts_for_rule = all_rhs_for_rule.split("|")
        print("breakdown_rhs: ")
        print(rhs_parts_for_rule)
        rhs_parts = []
        for part in rhs_parts_for_rule:
            part.strip()
            nt_or_t = part.split()
            print("nt_or_t breakdown_rhs: ")
            print(nt_or_t)
            rhs_parts.append(nt_or_t)
        print("rhs_parts")
        print(rhs_parts)
        return rhs_parts
            

    def parse_rules(self, all_rules):
        print("Parsing rules")
        for rule in all_rules:
            if rule != '':
                lhs_rhs = rule.split(":")
                lhs = lhs_rhs[0].strip()
                all_rhs_for_rule = lhs_rhs[1].strip()
                self.nt_list.append(lhs)
                #rhs_parts = breakdown_rhs(all_rhs_for_rule)
                rhs_parts_for_rule = all_rhs_for_rule.split("|")
                rhs_parts = []
                for part in rhs_parts_for_rule:
                    part.strip()
                    nt_or_t = part.split()
                    rhs_parts.append(nt_or_t)

                for rhs_part in rhs_parts:
                    final_rule = []
                    final_rule.append(lhs)
                    for x in rhs_part:
                        final_rule.append(x)
                    self.final_all_rules.append(final_rule)
        print(self.final_all_rules)
        return (self.final_all_rules)

    def ruleCheck_rhs_nt(self, rules_list):
        nt_set = set(self.nt_list)
        all_nt_rhs = set()
        for rule in rules_list:
            for i in range(1, len(rule)):
                if rule[i].isalpha() and rule[i][0].isupper():
                    all_nt_rhs.add(rule[i])
        for nt in all_nt_rhs:
            if nt not in nt_set:
                print ((" No rule present for NT: " , nt))
                return False
        return True 

    def probability_check(self, rules_list):
        nt = ""
        prob = 1.0
        for rule in rules_list:
            if rule[0] != nt:
                if prob.is_integer() and (prob < 0.5 or prob > 1.5):
                    print (("Probability != 1 for rule ", nt, "prob "))
                    return False
                prob = float(rule[len(rule) - 1])
                nt = rule[0]
            else:
                prob = prob + float(rule[len(rule) - 1])
        return True

    def verify_rules(self, rules_list):
        print("Verifying rules")
        rule_nt_rhs_status = self.ruleCheck_rhs_nt(rules_list)
        if rule_nt_rhs_status == False:
            return False
        
        prob_verification_status = self.probability_check(rules_list)
        if prob_verification_status == False:
            return False
        
        return True

    def handle_rule(self, line, delimitter, line_No):
        lineNo = str(line_No)
        str1 = ""
        line = line.split(delimitter)
        if line[0] != '':
            str1 += line[0].strip() + " STRING " + lineNo +"\n"
        str1 += delimitter + " OP "  + lineNo +"\n"
        rhs = line[1].strip().split(";")

        rhs_parts = rhs[0].strip().split()
        length = len(rhs_parts)
        for i in range(0,length):
            str1 += rhs_parts[i].strip()
            if i == length - 1:
                str1 += " DOUBLE " + lineNo +""
            else:
                str1 += " STRING " + lineNo +"\n"
        if(len(rhs) == 2 and rhs[1] == ''):
            str1 += "\n;" + " OP " + lineNo
        print (str1)
            
    def handle_sentence(self, line, line_No):
        lineNo = str(line_No)
        str1 = ""
        parts = line.strip().split('=')
        str1 += parts[0].strip() + " STRING " + lineNo +"\n"
        str1 += "=" + " OP " + lineNo +"\n"
        sent = parts[1].strip()
        curr = ''
        for word in sent.split():
            for letter in word:
                if not letter.isalpha():
                    if curr != '':
                        variants = self.root_word_variants[curr]
                        roots = " "
                        for root in variants:
                            if root != curr:
                                roots += root + " "
                        str1 += curr + " STRING " + lineNo + roots + "\n"
                        curr = ''
                    str1 += letter + " OP " + lineNo +"\n"
                else:
                    curr = curr + letter
            if curr != '':
                variants = self.root_word_variants[curr]
                roots = " "
                for root in variants:
                    if root != curr:
                        roots += root + " "
                str1 += curr + " STRING " + lineNo + roots + "\n"
                curr = ''

        str1 += "ENDFILE\n"
        print(str1)

    def print_output_datatypes(self, inp_arr):
        i = 0;
        print("Stemmer:")
        for line in inp_arr:
            i +=1
            str_line = line.split("#")
            line = str_line[0].strip()
            if line == '':
                continue;
            if line.find("=") != -1:
                #print "Handle Snet"
                self.handle_sentence(line, i)                
                #OutputSentence
            if line.find(":") != -1 or  line.find("|") != -1:
                delimiter = ":"
                if line.find("|") != -1:
                    delimiter = "|"
                #HandleRule
                self.handle_rule(line, delimiter, i)
            
            


#assuming the the grammar is binirizing.
    def create_lex_and_syn_table(self, rules_list):
        for rule in rules_list:
            if len(rule) == 3:
                #create lex table NT T probability
                self.lex[rule[0]][rule[1]] = rule[2]
            elif len(rule) == 4:
                #create syn table NT (T/NT) (T/NT) probability
                #self.syn[(rule[0], rule[1], rule[2])] = rule[3]
                self.syn[rule[0]][rule[1]][rule[2]] = rule[3]
        #print "Printing Lex: " 
        #self.printDict(self.lex)
        #print "Printing Syn: "
        #self.printDict(self.syn)
    

    def lemmatize(self):
        import re
        s = self.ip_sentence.strip().split("=")
        print("input sentence = "+s[1])
        s = re.sub(r'[^\w\s]','',s[1])
        print("sentence after punctuation removal= "+s)
        self.words = s.split()
        print(self.words)
        import nltk
        tokenized_text = nltk.word_tokenize(s)
        pos_tagged_s = nltk.pos_tag(tokenized_text)
        #print pos_tagged_s
        self.createWordVariants(pos_tagged_s)
  
    def getWordnetTagFromPosTag(self, tag):
        from nltk.corpus import wordnet as wn
        if tag.startswith('V'):
            return wn.VERB
        if tag.startswith('N'):
            return wn.NOUN
        if tag.startswith('RB'):
            return wn.ADV
        if tag.startswith('J'):
            return wn.ADJ
        return None

    def createWordVariants(self, pos_tagged_s):
        for w,pos in pos_tagged_s:
            #print "Extracting roots for ", w, " with pos ", pos
            wn_tag = self.getWordnetTagFromPosTag(pos)
            if wn_tag != None:
                #print "Considering word to morphy " , w, "pos " , pos
                self.root_word_variants[w] = wn._morphy(w.lower(), wn_tag)
            else:
                self.root_word_variants[w] = [(wnl.lemmatize(w.lower()))]
        #print "Printing root word variants"        
        #print self.root_word_variants

    def initializeDelta(self):
        i = 0
        for word in self.words:
            i += 1
            added = False
            #loop over variations
            #print "considering word :" , word
            for w in self.root_word_variants[word]:
                #print "Cheking for root ", w
                for nt in self.nt_list:
                    #print "Cheking for nlt: ", nt
                    if nt in self.lex and w in self.lex[nt]:
                        if added == True and nt in self.delta[i][i]:
                            if self.delta[i][i][nt] < self.lex[nt][w]:
                                self.delta[i][i][nt] = self.lex[nt][w]
                        else:
                            added = True
                            self.delta[i][i][nt] = self.lex[nt][w]
            if added == False:
                print (("FATAL ERROR: Not found NT for " , word))
        #print "Printing Delta:"
        #self.printDict(self.delta)

    def get_delta(self,x,y,z):
        if x in self.delta:
            if y in self.delta[x]:
                if z in self.delta[x][y]:
                    print(("b4 ret delta" , float(self.delta[x][y][z])))
                    return float(self.delta[x][y][z])
        return 0.0    

    def ckyParse(self):
        for span in range(2, len(self.words) + 1):
            for begin in range(1, len(self.words) - span + 2):
                end = begin + span - 1 
                for middle in range (begin, end):
                    for a in self.syn:
                        for b in self.syn[a]:
                            for c in self.syn[a][b]:
                                print(("val1: ", float(self.syn[a][b][c])))
                                p = float(self.syn[a][b][c]) * self.get_delta(begin, middle, b) * self.get_delta(middle+1,end,c)
                                print("p= " , p)
                                if p > self.get_delta(begin,end,a):
                                    #print"inside if :"
                                    self.delta[begin][end][a] = p
                                    self.chart[begin][end][a] = str(middle) + "_"+ b +"_"+ c 
        print("Delta Printing: ")
        self.printDict(self.delta)
        print("Chart Printing: ")
        #self.printDict(self.chart)
        #print("Length =" , len(self.words))

    def print_chart(self):
        print("Parsed Tree:")
        self.chart_drawing(1, len(self.words) , 'S', 0)
        output_prob = "P(w) = "
        i = 0
        for x in self.pOfW:
            if i == 0:
                output_prob += x
            else:
                output_prob += " * " + x
            i += 1
        output_prob += " = "+ str(self.delta[1][len(self.words)]['S'])
        print(output_prob)

    def chart_drawing(self, begin, end, nt1, numOfPipes):
        if (begin == end):
            index = begin
            if index > len(self.words):
                #print "Invalid index chart"
                return
                
            word = self.words[index-1]
            prob = self.delta[index][index][nt1] 
            #print (self.delta[index][index][nt1])
            strlastButOne = ""
            for i in range(0, numOfPipes):
                strlastButOne += "| \t"
            strlastButOne += nt1 + "\t" + str(prob)
            self.pOfW.append(prob)
            print (strlastButOne)
            strFinalLine = ""
            for i in range(0, numOfPipes+1):
                strFinalLine += "| \t"
            strFinalLine += self.words[index-1]
            print (strFinalLine)
        else:
            val = self.chart[begin][end][nt1];
            val_arr = val.split("_")
            middle = int(val_arr[0])
            nt2 = val_arr[1]
            nt3 = val_arr[2]
            strPipes = ""
            for i in range(0, numOfPipes):
                strPipes += "| \t"
            strPipes += nt1 + "\t" + self.syn[nt1][nt2][nt3]
            self.pOfW.append(self.syn[nt1][nt2][nt3])
            print (strPipes)
            pipesNum = numOfPipes + 1
            #print nt1 + " : " + nt2 + " " +nt3 + " " + self.syn[nt1][nt2][nt3]
            self.chart_drawing(begin, middle, nt2, pipesNum)
            self.chart_drawing(middle + 1, end, nt3, pipesNum)
                
    def convertToCNF(self,rules_list):
        # Algo as described at https://en.wikipedia.org/wiki/Chomsky_normal_form#Converting_a_grammar_to_Chomsky_normal_form
        rules_list = self.startSymbolAdder(rules_list)
        print("after startSymbolAdder\n" , rules_list)
        rules_list = self.terminalRemover(rules_list)
        print("after terminal remover\n", rules_list)
        rules_list = self.binarize(rules_list)
        print ("after binarize\n", rules_list)
        rules_list = self.unitRuleRemover(rules_list)
        print("after unitRuleRemover\n", rules_list)
        #print (rules_list)
        return rules_list
        
    def startSymbolAdder(self, rules_list):
        addStart = False
        for rule in rules_list:
            #Assuming that Standard Symbol 'S' is the start --> sentence indicator
            for x in range(1, len(rule)):
                if rule[x] == 'S':
                    addStart = True
        if addStart == True:
            rules_list = [['S0', 'S', '1.0']] + rules_list
            self.nt_list.append('S0')
        return rules_list

    def terminalRemover(self, rules_list):
        nt_set = set(self.nt_list)
        rules_to_add = []
        for rule in rules_list:
            if len(rule) > 3: # there are atleast two symbols on rhs
                for i in range(1, len(rule) - 1): # ignore the probability of the rule
                    if rule[i] not in nt_set:
                        new_nt = rule[i] + "_NT"
                        term = rule[i]
                        rule[i] = new_nt
                        if new_nt not in nt_set:
                            rules_to_add.append([new_nt, term, '1.0'])
                            self.nt_list.append
                            nt_set.add(new_nt)
        return rules_list + rules_to_add

    def binarizeOneRule(self, rule):
        new_nt = ''
        for index_NT in range(2, len(rule) - 1):
            new_nt += rule[index_NT]
            new_nt += "-"
        new_rule = [rule[0], rule[1], new_nt, rule[len(rule) - 1]]
        nextrule = [new_nt]
        for j in range(2,len(rule)-1):
            nextrule.append(rule[j])
        nextrule.append('1.0')
    
        return new_rule, nextrule
        

    def binarize(self, rules_list):
        binarized_rules = []
        for in_rule in rules_list:
            if(len(in_rule) > 4):
                rule = in_rule
                while len(rule) > 4: # there are more than 2 symbols on rhs
                    new_rule, rule = self.binarizeOneRule(rule)
                    binarized_rules.append(new_rule)
                    print(("rule len: " , rule , " " , len(rule)))
                binarized_rules.append(rule)     
            else:
                binarized_rules.append(in_rule)
        return binarized_rules
    
    def replaceNT(self, NT1, NT2, prob, rules_list): # replaces all occurences of NT2 to NT1 and multiplies with p of NT1 -> NT2
        for in_rule in rules_list:
            multiply = True
            if in_rule[0] == NT1: # if the rule is for NT1 dont multiply prob, its already correct.
                multiply = False
                
            for i in range(0, len(in_rule) - 1): # ignore probability
                if in_rule[i] == NT2:
                    in_rule[i] = NT1
                    if multiply:
                        in_rule[len(in_rule)-1] = str(prob * float(in_rule[len(in_rule)-1]))
        print("Modified rules")
        print (rules_list)
        

    def unitRuleRemover(self, rules_list):
        for in_rule in rules_list:
            if len(in_rule) == 3 and in_rule[1][0].isupper(): # if we are going from a NT to NT its a unit rule
                if in_rule[0] != in_rule[1]: # ignore A->A rules for now
                    self.replaceNT(in_rule[0], in_rule[1], float(in_rule[2]), rules_list)
        new_rules = []
        for in_rule in rules_list:
            if len(in_rule) == 3 and in_rule[0] == in_rule[1]:
                continue; # ignore identity rules
            new_rules.append(in_rule)
        return new_rules


def main():
    obj = ViterbiParser()
    inputStr, inp_arr = obj.read_input()
    if inputStr == None:
        print ("Input Error")
        return
    print("verifying input:")
    print(inputStr)
    all_rules = obj.get_all_rules_array_from_ip(inputStr)
    print(all_rules)
    rules_list = obj.parse_rules(all_rules) 
    verify_status = obj.verify_rules(rules_list)
    if verify_status == False:
        print ("Input Error")
        return
    
    #print "Old rules"
    print(rules_list)
    #final_rules_list = rules_list
    final_rules_list = obj.convertToCNF(rules_list)
    obj.lemmatize()
    obj.create_lex_and_syn_table(final_rules_list)
    obj.initializeDelta()
    obj.ckyParse()
    
    print(("inp_arr", inp_arr))
    #for i in range(1,10):
        #print
    obj.print_output_datatypes(inp_arr)
    obj.print_chart()
    return 1
    
main()