#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 19:35:31 2019

@author: ivanskya
"""

import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.set('foo', 'bar')
print( r.get('foo') )
print( r.get('foo') )
print( r.get('foo') )
print( r.get('foo') )
r.set('foo', 'bar1')
r.set('foo', 'bar2')
r.set('foo', 'bar3')
print( r.get('foo') )
print( r.get('foo') )
print( r.get('foo') )
print( r.get('adam') )

a = r.get('abc')

if (a is None):
    print('a is None')