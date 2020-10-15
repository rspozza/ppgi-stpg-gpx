#!/usr/bin/env python
# coding: utf-8

# In[]:

import sys; sys.path.append('..')


# In[2]:


from graph import Graph


# In[3]:


from collections import deque, defaultdict


# In[4]:


# The steps 1 and 2 can be done in just one function like

def compose(red, blue):
    '''
    Parameters:
    ----------
        red, blue : Graph

    Return:
    -------
        g_union, g_common, g_star : Graph
    '''

    g_union  = Graph()
    g_common = Graph()
    g_star   = Graph()


    for v, u in red.gen_undirect_edges():
        g_union.add_edge(v,u)

        if not blue.has_edge(v,u):
            g_star.add_edge(v,u)

    for v, u in blue.gen_undirect_edges():
        g_union.add_edge(v,u)

        if red.has_edge(v,u):
            g_common.add_edge(v,u)
        else:
            g_star.add_edge(v,u)


    return g_union, g_common, g_star


# In[5]:


class Component:

    def __init__(self, head):
        self.head = head
        self.tail = None
        self.prev = {head : None}
        self.portal = set([head])


# In[ ]:





# In[6]:


def connected_componentes(red : Graph, blue : Graph, start : 'node'):

    g_union, g_common, g_star = compose(red, blue)

    stack = deque([start])
    previous = {start : start} # instead {start : None}
    red_components  = list()
    blue_components = list()

    def chase(whatever, head, tail=None, component = None):
        if tail is None:
            v = head
        else:
            v = tail

        for w in whatever.adjacent_to(v):
            if w not in previous:
                previous[w] = v
            if w not in component.prev:
                component.prev[w] = v

                if (w in red) and (w in blue):
                    stack.append(w)
                    component.portal.add(w)
                else:
                    chase(whatever, head, tail=w, component=component)

    while stack:
        u = stack.pop()

        for w in g_union.adjacent_to(u):
            if w in previous:
                continue

            if red.has_edge(u,w) and blue.has_edge(u,w):
                stack.append(w)
                previous[w] = previous[u] # prev f = prev[a] == B ou C ??
            elif red.has_edge(u,w):
                previous[w] = u
                component = Component(u)
                component.prev[w] = u
                chase(red, u, tail=w, component = component)
                red_components.append(component)
            elif blue.has_edge(u,w):
                previous[w] = u
                component = Component(u)
                component.prev[w] = u
                chase(blue, u, tail=w, component = component)
                blue_components.append(component)

        print(stack)

    return blue_components, red_components


# In[7]:


aa = Graph(edges={
    'E' : {'C' : 5},
    'C' : {'E' : 5 , 'D' : 4},
    'D' : {'C' : 4 , 'F' : 9},
    'F' : {'D' : 9 , 'A' : 3},
    'A' : {'F' : 3}
})

bb = Graph(edges={
    'E' : {'C' : 4},
    'C' : {'E' : 4,  'B' : 10},
    'B' : {'C' : 10, 'A' : 11},
    'A' : {'B' : 11},
})

first, second = connected_componentes(aa, bb, 'E')


# In[8]:


first[0].portal


# In[9]:


first[0].prev


# In[10]:


second[0].portal


# In[11]:


second[0].prev


# ---

# In[12]:


aa = Graph(edges={
    'E' : {'B' : 1},
    'B' : {'E' : 1, 'A' : 1},
    'A' : {'B' : 1, 'F' : 1},
    'F' : {'A' : 1, 'H' : 1},
    'H' : {'F' : 1, 'J' : 1},
    'J' : {'H' : 1}
})

bb = Graph(edges={
    'E' : {'D' : 1},
    'D' : {'E' : 1, 'C' : 1},
    'C' : {'D' : 1, 'A' : 1},
    'A' : {'C' : 1, 'F' : 1},
    'F' : {'I' : 1, 'A' : 1},
    'I' : {'J' : 1, 'F' : 1},
    'J' : {'I' : 1}
})

first, second = px(aa, bb, 'E')


# In[13]:


first


# In[14]:


first[0].portal


# In[15]:


first[1].portal


# In[16]:


second[0].portal


# In[17]:


second[1].portal


# In[18]:


second[0].prev


# In[19]:


second[1].prev


# In[20]:


first[0].prev


# In[21]:


first[1].prev


# ---

# In[23]:


aa = Graph(edges={
    'E' : {'B' : 1},
    'B' : {'E' : 1, 'A' : 1},
    'A' : {'B' : 1, 'F' : 1},
    'F' : {'A' : 1, 'H' : 1},
    'H' : {'F' : 1, 'J' : 1},
    'J' : {'H' : 1}
})

bb = Graph(edges={
    'E' : {'D' : 1},
    'D' : {'E' : 1, 'C' : 1},
    'C' : {'D' : 1, 'A' : 1},
    'A' : {'C' : 1, 'I' : 1},
    'I' : {'J' : 1, 'A' : 1},
    'J' : {'I' : 1}
})

first, second = connected_componentes(aa, bb, 'E')


# In[24]:


first


# In[26]:


first[0].portal


# In[27]:


first[1].portal


# In[28]:


second[0].portal


# In[29]:


second[1].portal


# In[ ]:




