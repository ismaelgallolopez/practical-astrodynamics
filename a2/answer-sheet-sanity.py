#!/usr/bin/env python3

import os
import sys
import numpy

class bc:
    DGR = '\033[90m' # dark GREY
    RED = '\033[91m' # RED
    GRE = '\033[92m' # GREEN
    YEL = '\033[93m' # YELLOW
    PUR = '\033[94m' # PURPLE
    PNK = '\033[95m' # PINK
    CYA = '\033[96m' # CYAN
    LGR = '\033[97m' # light GREY
    BLK = '\033[98m' # BLACK
    RES = '\033[0m'  # RESET COLOR5

HEADTAIL_LEN=5
FMT="%19.12e"

# wrapper for stderr printing
def say(s,colour=bc.LGR):
  sys.stderr.write("{}{}{}\n" .format(colour,s,bc.RES))
# colorize for errors
def say_error(s):
  say(s,colour=bc.RED)
# colorize for notifications
def say_warning(s):
  say(s,colour=bc.PUR)
# colorize for debugging, flagged
def say_debug(s,debug=True):
  if debug:
    say(s,colour=bc.YEL)
# colorize for notifications
def say_notice(s):
  say(s,colour=bc.GRE)
# show basic info of a variable
def peek_str(a,tab=0):
  t=type(a).__name__
  out=""
  if t == "str":
    out+="({:>8}) len={} value={}".format(t,len(a),a)
  elif t == "ndarray":
    if a.size<10:
      out+="({:>8}) size={} shape={} value={}".format(t,a.size,a.shape,a)
    else:
      out+="({:>8}) size={} shape={}".format(t,a.size,a.shape)
  elif t == "list":
    if len(a)<10:
      out+="({:>8}) len={} value={}".format(t,len(a),a)
    else:
      out+="({:>8}) len={}".format(t,len(a))
  elif t in ["float","int","bool","tuple","numpy.float64"]:
    out+="({:>8}) value={}".format(t,a)
  elif t == "dict":
    out+="({:>8}) contains:\n".format(t)
    for k,v in a.items():
      out+=" "*(tab+6)+"{:>17} : {:}\n".format(k,peek_str(v,tab+6))
  elif hasattr(a, '__size__') and hasattr(a, '__shape__'):
    out+="({:>8}) size={} shape={}".format(t,a.size,a.shape)
  elif hasattr(a, '__size__'):
    out+="({:>8}) size={}".format(t,a.size)
  elif t == "Satrec":
    out+="({:>8}):\n".format(t)
    for i in ['jdsatepoch','jdsatepochF','epochyr','epochdays']:
      out+=" "*(tab+6)+"{:>17} : {:}\n".format(i,peek_str(getattr(a,i),tab+6))
  else:
    out+="({}) type unknown".format(t)
  return out
def peek(a,d='unknown',debug=True):
  say_debug("{:>20} : {}".format(d,peek_str(a)),debug)
# cleanly show variables
def clean_str(a):
  ta=type(a)
  if hasattr(a, "__len__") and not ta is str:
    ti=type(a[0])
    if ti is str:
      join_char="\n"
    else:
      join_char=" "
    out=join_char.join([f"{clean_str(i)}" for i in a])
  else:
    out="{}".format(a)
  return out
# convert string with one or more numeric values to a list of floats
def str2float(text,sepchar=' '):
    for item in text.split(sepchar):
        try:
            yield float(item)
        except ValueError:
            pass
# load yaml parameters
def load_yaml_from_file(filename,debug=False):
  from yaml import  safe_load
  # load yaml file
  with open(filename, 'r') as file:
    data = safe_load(file)
  # patch debug option
  if 'debug' in data:
    debug=data['sb_debug']
  # convert as necessary
  for k in data:
    data[k]=convert_types(k,data[k],debug)
  # done
  return data
# handle multiple data types, based on key:
# `ST_NAME`
# ... with:
# - `S` one of:
#   - `s` for scalar
#   - `l` for vectors (Python lists)
# - `T` one of:
#   - `f` for floating point numbers
#   - `i` for integer numbers
#   - `b` for boolean values (true/false)
#   - `s` for strings (text)
# - `NAME` is a general string with the name of the key
def convert_types(key,value,debug=False):
  # get sequence and type from key
  seq=resolve_sequences(key,debug)
  typ=resolve_types(    key,debug)
  # check it this data entry is a list
  if isinstance(value,list):
    # ensure agreement with sequence from key
    if seq=='scalar':
      raise Exception(f"key '{key}' specifies sequence '{seq}' while value is actually a list")
    say_debug(f"Converting vector {key} with values '{value}' to {typ}",debug)
    if typ=='str':
      # need to strip strings
      out=[str(v).strip() for v in value]
    else:
      # scalar conversion
      out=[eval(f"{typ}(v)") for v in value]
    if seq=='np.array':
      say_debug(f"Converting vector {key} to {seq}",debug)
      return numpy.array(out)
    else:
      return out
  else:
    # ensure agreement with sequence from key
    if seq=='list':
      raise Exception(f"key '{key}' specifies sequence '{seq}' while value is actually not a list")
    say_debug(f"Converting scalar {key} with value '{peek_str(value)}' to {typ}",debug)
    if typ=='str':
      # need to strip strings
      out=str(value).strip()
    else:
      # scalar conversion
      out=eval(f"{typ}(value)")
    # handle single-entry vectors
    if not seq=='scalar':
      say_debug(f"Converting scalar {key} with single entry to {seq}",debug)
      out=eval(f"{seq}(value)")
    else:
      return out
def cbool(val):
  if isinstance(val,str):
    # https://stackoverflow.com/a/18472142
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1','one'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0','zero'):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))
  else:
    return bool(val)
def resolve_sequences(key,debug=False):
  say_debug(f"Resolving sequence of key {key}",debug)
  t=key.split('_')[0][0]
  if t=='s': return 'scalar'
  if t=='a': return 'np.array'
  if t=='l': return 'list'
  raise Exception(f"Cannot handle sequence identifier '{t}' in key '{key}'")
def resolve_types(key,debug=False):
  say_debug(f"Resolving type of key {key}",debug)
  t=key.split('_')[0][1]
  if t=='s': return 'str'
  if t=='f': return 'float'
  if t=='i': return 'int'
  if t=='b': return 'cbool'
  raise Exception(f"Cannot handle type identifier '{t}' in key '{key}'")

debug=False
filename='answer-sheet.yaml'
peek(load_yaml_from_file(os.path.join(os.path.dirname(__file__),filename),debug=debug),filename)
