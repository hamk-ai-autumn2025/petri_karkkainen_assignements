# -*- coding: utf-8 -*-
"""
Advanced Test Runner for Any Python Code.

This script automatically discovers and tests functions in any Python file,
including edge cases like very long strings, infinity, NaN, etc.
"""

import importlib
import sys
import os
import inspect
from typing import Any, Dict, List, Callable


def analyze_code_file(file_path: str) -> List[str]:
    """Analyze a Python file and return all function names."""
    directory = os.path.dirname(file_path)
    if directory not in sys.path:
        sys.path.insert(0, directory)

    module_name = os.path.splitext(os.path.basename(file_path))[0]

    try:
        module = importlib.import_module(module_name)

        functions = []
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and obj.__module__ == module.__name__:
                functions.append(name)

        return functions
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return []


def test_with_edge_cases(func: Callable, func_name: str) -> Dict[str, Any]:
    """Test a function with various edge cases."""
    results = {
        'basic': {'success': False, 'error': None},
        'long_string': {'success': False, 'error': None},
        'unicode_arabic': {'success': False, 'error': None},
        'unicode_chinese': {'success': False, 'error': None},
        'infinity': {'success': False, 'error': None},
        'negative_infinity': {'success': False, 'error': None},
        'nan': {'success': False, 'error': None},
        'zero_division': {'success': False, 'error': None}
    }

    # Basic test
    try:
        # Try with basic inputs based on common function patterns
        if 'add' in func_name.lower() or 'sum' in func_name.lower():
            result = func(1, 2)
        elif 'multiply' in func_name.lower() or 'mul' in func_name.lower():
            result = func(3, 4)
        elif 'divide' in func_name.lower() or 'div' in func_name.lower():
            result = func(10, 2)
        elif 'process' in func_name.lower() or 'convert' in func_name.lower():
            result = func("test")
        else:
            # Try common patterns
            try:
                result = func("test")
            except TypeError:
                try:
                    result = func(1, 2)
                except TypeError:
                    try:
                        _ = func(1)  # Use _ to indicate unused variable
                    except Exception as e:
                        _ = func()
                        results['basic']['error'] = str(e)

        results['basic']['success'] = True
    except Exception as e:
        results['basic']['error'] = str(e)

    # Test with very long string
    try:
        long_string = "A" * 10000  # Very long string
        if 'add' in func_name.lower() or 'sum' in func_name.lower():
            result = func(long_string, "test")
        elif 'process' in func_name.lower() or 'convert' in func_name.lower():
            result = func(long_string)
        else:
            result = func(long_string)
        results['long_string']['success'] = True
    except Exception as e:
        results['long_string']['error'] = str(e)

    # Test with Arabic Unicode
    try:
        arabic_text = "مرحبا بالعالم" * 100
        if 'add' in func_name.lower() or 'sum' in func_name.lower():
            result = func(arabic_text, "test")
        elif 'process' in func_name.lower() or 'convert' in func_name.lower():
            result = func(arabic_text)
        else:
            result = func(arabic_text)
        results['unicode_arabic']['success'] = True
    except Exception as e:
        results['unicode_arabic']['error'] = str(e)

    # Test with Chinese Unicode
    try:
        chinese_text = "你好世界" * 100
        if 'add' in func_name.lower() or 'sum' in func_name.lower():
            result = func(chinese_text, "test")
        elif 'process' in func_name.lower() or 'convert' in func_name.lower():
            result = func(chinese_text)
        else:
            result = func(chinese_text)
        results['unicode_chinese']['success'] = True
    except Exception as e:
        results['unicode_chinese']['error'] = str(e)

    # Test with infinity (for math functions)
    try:
        if 'add' in func_name.lower() or 'sum' in func_name.lower():
            result = func(float('inf'), 1)
        elif 'divide' in func_name.lower() or 'div' in func_name.lower():
            result = func(float('inf'), 2)
        elif 'multiply' in func_name.lower() or 'mul' in func_name.lower():
            result = func(float('inf'), 2)
        else:
            result = func(float('inf'))
        results['infinity']['success'] = True
    except Exception as e:
        results['infinity']['error'] = str(e)

    # Test with negative infinity
    try:
        if 'add' in func_name.lower() or 'sum' in func_name.lower():
            result = func(float('-inf'), 1)
        elif 'divide' in func_name.lower() or 'div' in func_name.lower():
            result = func(float('-inf'), 2)
        elif 'multiply' in func_name.lower() or 'mul' in func_name.lower():
            result = func(float('-inf'), 2)
        else:
            result = func(float('-inf'))
        results['negative_infinity']['success'] = True
    except Exception as e:
        results['negative_infinity']['error'] = str(e)

    # Test with NaN
    try:
        if 'add' in func_name.lower() or 'sum' in func_name.lower():
            result = func(float('nan'), 1)
        elif 'divide' in func_name.lower() or 'div' in func_name.lower():
            result = func(float('nan'), 2)
        elif 'multiply' in func_name.lower() or 'mul' in func_name.lower():
            result = func(float('nan'), 2)
        else:
            result = func(float('nan'))
        results['nan']['success'] = True
    except Exception as e:
        results['nan']['error'] = str(e)

    # Test for zero division (if applicable)
    try:
        if 'divide' in func_name.lower() or 'div' in func_name.lower():
            result = func(10, 0)  # This might raise an exception
        results['zero_division']['success'] = True
    except ZeroDivisionError:
        # This is expected for division functions
        results['zero_division']['success'] = True
        error_msg = "ZeroDivisionError (expected for division functions)"
        results['zero_division']['error'] = error_msg
    except Exception as e:
        results['zero_division']['error'] = str(e)

    return results


def run_advanced_tests_on_file(file_path: str) -> Dict[str, Any]:
    """Run advanced tests on a Python file and return detailed results."""
    print("\n" + "="*70)
    print(f"ADVANCED TESTING: {file_path}")
    print("="*70)

    # Analyze the file
    functions = analyze_code_file(file_path)
    print(f"Discovered {len(functions)} functions: {functions}")

    if not functions:
        print("No functions found in the file!")
        return {"file": file_path, "functions": [], "results": {}}

    # Import the module
    directory = os.path.dirname(file_path)
    if directory not in sys.path:
        sys.path.insert(0, directory)

    module_name = os.path.splitext(os.path.basename(file_path))[0]
    module = importlib.import_module(module_name)

    all_results = {}

    for func_name in functions:
        print(f"\n--- Testing Function: {func_name} ---")

        func = getattr(module, func_name)
        results = test_with_edge_cases(func, func_name)

        # Print results for this function
        for test_type, result in results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"  {test_type}: {status}")
            if result['error']:
                print(f"    Error: {result['error']}")

        all_results[func_name] = results

    # Summary
    print("\n" + "="*70)
    print(f"DETAILED SUMMARY FOR: {file_path}")
    print("="*70)

    total_tests = 0
    passed_tests = 0

    for func_name, results in all_results.items():
        print(f"\nFunction: {func_name}")
        func_passed = 0
        func_total = 0

        for test_type, result in results.items():
            total_tests += 1
            func_total += 1
            if result['success']:
                passed_tests += 1
                func_passed += 1

        print(f"  Passed: {func_passed}/{func_total}")

    overall_success_rate = (passed_tests / max(1, total_tests)) * 100
    msg = f"\nOVERALL: {passed_tests}/{total_tests} tests "
    msg += f"passed ({overall_success_rate:.1f}%)"
    print(msg)

    if passed_tests == total_tests:
        print("🎉 PERFECT! All edge cases handled correctly!")
    else:
        print("⚠️  Some edge cases need attention. Check detailed results above.")

    return {
        "file": file_path,
        "functions": functions,
        "results": all_results,
        "total_tests": total_tests,
        "passed_tests": passed_tests
    }


def main():
    """Main function to run advanced tests on specified files."""
    if len(sys.argv) < 2:
        msg = "Usage: python final_compliant_test_runner.py "
        msg += "<file1.py> [file2.py] [file3.py] ..."
        print(msg)
        msg = "Example: python final_compliant_test_runner.py "
        msg += "arabic_code.py chinese_code.py"
        print(msg)
        return

    all_results = []

    for file_path in sys.argv[1:]:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        result = run_advanced_tests_on_file(file_path)
        all_results.append(result)

    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)

    total_tests = 0
    total_passed = 0

    for result in all_results:
        msg = f"{result['file']}: {result['passed_tests']}/"
        msg += f"{result['total_tests']} passed"
        print(msg)
        total_tests += result['total_tests']
        total_passed += result['passed_tests']

    if total_tests > 0:
        final_rate = (total_passed / total_tests) * 100
        msg = f"\nGRAND TOTAL: {total_passed}/{total_tests} tests "
        msg += f"passed ({final_rate:.1f}%)"
        print(msg)

        if total_passed == total_tests:
            print("🎉 EXCELLENT! All code handles edge cases perfectly!")
        else:
            print("⚠️  Consider improving edge case handling in your code.")


if __name__ == "__main__":
    main()
