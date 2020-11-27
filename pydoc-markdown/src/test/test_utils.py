
def assert_text_equals(a, b):
  assert '\n'.join([x.rstrip() for x in a.strip().split('\n')]) == \
         '\n'.join([x.rstrip() for x in b.strip().split('\n')])
