#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 19:35:31 2019

@author: ivanskya
"""

import redis

r = redis.Redis(host='localhost', port=6379, db=3)
r.flushall()

r.lpush('user_log', 'bar')
print( r.lpop('foo') )
print( r.lpop('foo') )
print( r.lpop('foo') )
print( r.lpop('foo') )
r.lpush('foo', 'bar1')
r.lpush('foo', 'bar2')
r.lpush('foo', 'bar3')
print( r.rpop('foo') )
print( r.rpop('foo') )
print( r.rpop('foo') )
print( r.rpop('adam') )
