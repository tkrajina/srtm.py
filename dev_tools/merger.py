import json
import pickle


v1_1a = {}
v1_3a = {}
v2_1a = {}
v2_3a = {}
v3 = {}

combined = {}

keys = set()


# Read in each file
with open('v1_1a.txt') as f:
    tiles = f.read()
for line in tiles.splitlines():
    v1_1a[line] = True
    keys.add(line)


with open('v1_3a.txt') as f:
    tiles = f.read()
for line in tiles.splitlines():
    key, _, value = line.partition(', ')
    v1_3a[key] = value
    keys.add(key)

with open('v2_1a.txt') as f:
    tiles = f.read()
for line in tiles.splitlines():
    key, _, value = line.partition(', ')
    v2_1a[key] = value
    keys.add(key)

with open('v2_3a.txt') as f:
    tiles = f.read()
for line in tiles.splitlines():
    key, _, value = line.partition(', ')
    v2_3a[key] = value
    keys.add(key)

with open('v3.txt') as f:
    tiles = f.read()
for line in tiles.splitlines():
    v3[line] = True
    keys.add(line)


# Merge
for key in keys:
    ver1_1arc = False
    ver1_3arc = ''
    ver2_1arc = ''
    ver2_3arc = ''
    ver3 = False
    if key in v1_1a: ver1_1arc = True
    if key in v1_3a: ver1_3arc = v1_3a[key]
    if key in v2_1a: ver2_1arc = v2_1a[key]
    if key in v2_3a: ver2_3arc = v2_3a[key]
    if key in v3: ver3 = True
    combined[key] = (ver1_1arc, ver1_3arc, ver2_1arc, ver2_3arc, ver3)


# Write out serialized file options
with open('srtm.json', 'w') as fp:
    json.dump(combined, fp, sort_keys=True)
with open('srtm.pickle','wb') as fp:
    pickle.dump(combined, fp)



