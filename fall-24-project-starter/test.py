from interpreterv2 import Interpreter

if __name__ == "__main__":
    program = """
    func test() { return; }
    func aland() { return; }
    func aland(a, b, c) { return; }
    func larry(x, y) { return; }
    func emily(z) { return; }
    func main() {
  var x;
  x = 5;
  var y;
  y = 10;
  var z;
  var d;
  var e;
  z = x + y;
  d = inputi("Enter a number: ");
  e = inputi("Enter another: ") + d;
  print(z + e, "! Here is your number plus 15!");
  var nullity;
  nullity = !false;
  if (nullity) {
    var test;
    test = 10;
    print(inputi("Enter: ") + test);
  } else {
    print("Fuck you monkey.");
  }
  print(true);
}"""

    program2 = """
  func main() {
  var i;
  var t;
  t = 1;
  print(t);
  for (i = 0; i < 10; i = i + 1) {
    print("t: ", t / 2);
    t = t + 2;
  }
  print(t);
  }
    """

    program2_2 = """
func main() {
  var i;
  var t;
  t = 1;
  print(t);
  for (i = 0; i < 10; i = i + 1) {
    print("t: ", t / 2);
    var t;
    t = 0;
    t = t + 2;
  }
  print(t);
  }
    """

    program3 = """
    func main() {
      var a;
      a = 10;
      print(a);
      if (true) {
        print(a);
        var a;
        a = "test";
        print(a);
      }
      print(a);
    }
    """

    program4 = """
    func times_two(x) {
      print(x * 2);
      return x * 2;
    }
    func times(x, y) {
      print(x * y);
    }
    func times_four(x) {
      var a;
      a = times_two(times_two(x));
      print("res: ", a);
    }
    func test(x) {
      var x;
      x = 10;
      print(x);
    }
    func main() {
      var a;
      a = 5;
      test(a);
      print("a: ", a);
      times_two(a);
      times(a, a + 6);
      times_four(a * 2);
    }
    """

    program5 = """
    func factorial(x) {
      if (x == 1) {
        return 1;
      }
      return x * factorial(x - 1);
    }

    func main() {
    var a;
    a = 3;
    var res;
    print(a);
    res = factorial(a * 2);
    print(res);
    }
    """

    program6 = """
func catalan(n) {
if (n <= 1) {
return 1;
}
var res;
res = 0;
var i;
for (i = 0; i < n; i = i + 1) {
var left;
var right;
left = catalan(i);
right = catalan(n - i - 1);
res = res + (left * right);
}
return res;
}

func main() {
var n;
n = 5;
var i;
for (i = 0; i <= n; i = i + 1) {
print(catalan(i));
}
}

/* OUT CORRECT OUTPUT
1
1
2
5
14
42
OUT */
    """

    program7 = """
    func fib(n) {
      if (n <= 2) {
        return 1;
      }
      return fib(n - 2) + fib(n - 1);
    }

    func main() {
      var a;
      a = 3;
      print(fib(15));
    }
    """

    program_scratch = """
func main() {
 print(catalan(4));
}

func catalan(n) {
	return catalan_help(n, 0, 0);
}

func catalan_help(n, ans, j) {
 if (n < 2) {
  return 1;
 } else {
  for (j = j;j < n; j = j + 1) {
   ans = ans + catalan(j) * catalan(n - j - 1);
  }
  return ans;
 }
}
    """

    interpreter = Interpreter()
    interpreter.run(program_scratch)