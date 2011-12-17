(function(program, execJS) { execJS(program) })(function(module, exports, require) { #{source}
}, function(program) {
  var output;
  var print = function(string) {
    process.stdout.write('' + string + '\n');
  };
  try {
    result = program();
    print('')
    if (typeof result == 'undefined' && result !== null) {
      print('["ok"]');
    } else {
      try {
        print(JSON.stringify(['ok', result]));
      } catch (err) {
        print('["err"]');
      }
    }
  } catch (err) {
    print(JSON.stringify(['err', '' + err]));
  }
});
