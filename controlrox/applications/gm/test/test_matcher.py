"""Unit tests for GM Controller Matcher.

This test suite provides comprehensive testing of the GmControllerMatcher
for identifying and matching GM-specific PLC controller patterns.
"""
import unittest


from controlrox.applications.gm.matcher import GmControllerMatcher
from controlrox.applications.gm.gm import GmController
from controlrox.services import ControllerMatcher


class TestGmControllerMatcherInheritance(unittest.TestCase):
    """Test cases for GmControllerMatcher inheritance."""

    def test_inherits_from_controller_matcher(self):
        """Test GmControllerMatcher inherits from ControllerMatcher."""
        self.assertTrue(issubclass(GmControllerMatcher, ControllerMatcher))


class TestGmControllerMatcherConstructor(unittest.TestCase):
    """Test cases for controller constructor method."""

    def test_get_controller_constructor_returns_gm_controller(self):
        """Test get_controller_constructor returns GmController class."""
        constructor = GmControllerMatcher.get_controller_constructor()

        self.assertEqual(constructor, GmController)
        self.assertTrue(issubclass(constructor, GmController.__bases__[1]))


class TestGmControllerMatcherDatatypePatterns(unittest.TestCase):
    """Test cases for datatype pattern matching."""

    def test_get_datatype_patterns_returns_list(self):
        """Test get_datatype_patterns returns a list."""
        patterns = GmControllerMatcher.get_datatype_patterns()

        self.assertIsInstance(patterns, list)

    def test_get_datatype_patterns_not_empty(self):
        """Test get_datatype_patterns returns non-empty list."""
        patterns = GmControllerMatcher.get_datatype_patterns()

        self.assertGreater(len(patterns), 0)

    def test_datatype_patterns_include_version(self):
        """Test datatype patterns include zz_Version."""
        patterns = GmControllerMatcher.get_datatype_patterns()

        self.assertIn('zz_Version', patterns)

    def test_datatype_patterns_include_prompt(self):
        """Test datatype patterns include zz_Prompt."""
        patterns = GmControllerMatcher.get_datatype_patterns()

        self.assertIn('zz_Prompt', patterns)

    def test_datatype_patterns_include_pfe_alarm(self):
        """Test datatype patterns include zz_PFEAlarm."""
        patterns = GmControllerMatcher.get_datatype_patterns()

        self.assertIn('zz_PFEAlarm', patterns)

    def test_datatype_patterns_include_toggle(self):
        """Test datatype patterns include za_Toggle."""
        patterns = GmControllerMatcher.get_datatype_patterns()

        self.assertIn('za_Toggle', patterns)

    def test_all_datatype_patterns_are_strings(self):
        """Test all datatype patterns are strings."""
        patterns = GmControllerMatcher.get_datatype_patterns()

        for pattern in patterns:
            self.assertIsInstance(pattern, str)


class TestGmControllerMatcherModulePatterns(unittest.TestCase):
    """Test cases for module pattern matching."""

    def test_get_module_patterns_returns_list(self):
        """Test get_module_patterns returns a list."""
        patterns = GmControllerMatcher.get_module_patterns()

        self.assertIsInstance(patterns, list)

    def test_get_module_patterns_not_empty(self):
        """Test get_module_patterns returns non-empty list."""
        patterns = GmControllerMatcher.get_module_patterns()

        self.assertGreater(len(patterns), 0)

    def test_module_patterns_include_sz_wildcard(self):
        """Test module patterns include sz_* wildcard."""
        patterns = GmControllerMatcher.get_module_patterns()

        self.assertIn('sz_*', patterns)

    def test_module_patterns_include_zz_wildcard(self):
        """Test module patterns include zz_* wildcard."""
        patterns = GmControllerMatcher.get_module_patterns()

        self.assertIn('zz_*', patterns)

    def test_module_patterns_include_cg_wildcard(self):
        """Test module patterns include cg_* wildcard."""
        patterns = GmControllerMatcher.get_module_patterns()

        self.assertIn('cg_*', patterns)

    def test_module_patterns_include_zs_wildcard(self):
        """Test module patterns include zs_* wildcard."""
        patterns = GmControllerMatcher.get_module_patterns()

        self.assertIn('zs_*', patterns)

    def test_all_module_patterns_are_strings(self):
        """Test all module patterns are strings."""
        patterns = GmControllerMatcher.get_module_patterns()

        for pattern in patterns:
            self.assertIsInstance(pattern, str)

    def test_module_patterns_use_wildcards(self):
        """Test module patterns use wildcard notation."""
        patterns = GmControllerMatcher.get_module_patterns()

        # At least some patterns should have wildcards
        has_wildcards = any('*' in pattern for pattern in patterns)
        self.assertTrue(has_wildcards, "Expected wildcard patterns for modules")


class TestGmControllerMatcherProgramPatterns(unittest.TestCase):
    """Test cases for program pattern matching."""

    def test_get_program_patterns_returns_list(self):
        """Test get_program_patterns returns a list."""
        patterns = GmControllerMatcher.get_program_patterns()

        self.assertIsInstance(patterns, list)

    def test_get_program_patterns_not_empty(self):
        """Test get_program_patterns returns non-empty list."""
        patterns = GmControllerMatcher.get_program_patterns()

        self.assertGreater(len(patterns), 0)

    def test_program_patterns_include_mcp(self):
        """Test program patterns include MCP."""
        patterns = GmControllerMatcher.get_program_patterns()

        self.assertIn('MCP', patterns)

    def test_program_patterns_include_pfe(self):
        """Test program patterns include PFE."""
        patterns = GmControllerMatcher.get_program_patterns()

        self.assertIn('PFE', patterns)

    def test_program_patterns_include_groups(self):
        """Test program patterns include GROUP1 and GROUP2."""
        patterns = GmControllerMatcher.get_program_patterns()

        self.assertIn('GROUP1', patterns)
        self.assertIn('GROUP2', patterns)

    def test_program_patterns_include_hmi(self):
        """Test program patterns include HMI1 and HMI2."""
        patterns = GmControllerMatcher.get_program_patterns()

        self.assertIn('HMI1', patterns)
        self.assertIn('HMI2', patterns)

    def test_all_program_patterns_are_strings(self):
        """Test all program patterns are strings."""
        patterns = GmControllerMatcher.get_program_patterns()

        for pattern in patterns:
            self.assertIsInstance(pattern, str)


class TestGmControllerMatcherSafetyProgramPatterns(unittest.TestCase):
    """Test cases for safety program pattern matching."""

    def test_get_safety_program_patterns_returns_list(self):
        """Test get_safety_program_patterns returns a list."""
        patterns = GmControllerMatcher.get_safety_program_patterns()

        self.assertIsInstance(patterns, list)

    def test_get_safety_program_patterns_not_empty(self):
        """Test get_safety_program_patterns returns non-empty list."""
        patterns = GmControllerMatcher.get_safety_program_patterns()

        self.assertGreater(len(patterns), 0)

    def test_safety_program_patterns_include_common(self):
        """Test safety program patterns include s_Common."""
        patterns = GmControllerMatcher.get_safety_program_patterns()

        self.assertIn('s_Common', patterns)

    def test_safety_program_patterns_include_segments(self):
        """Test safety program patterns include s_Segment1 and s_Segment2."""
        patterns = GmControllerMatcher.get_safety_program_patterns()

        self.assertIn('s_Segment1', patterns)
        self.assertIn('s_Segment2', patterns)

    def test_all_safety_program_patterns_are_strings(self):
        """Test all safety program patterns are strings."""
        patterns = GmControllerMatcher.get_safety_program_patterns()

        for pattern in patterns:
            self.assertIsInstance(pattern, str)

    def test_safety_program_patterns_start_with_s_prefix(self):
        """Test all safety program patterns start with 's_' prefix."""
        patterns = GmControllerMatcher.get_safety_program_patterns()

        for pattern in patterns:
            self.assertTrue(pattern.startswith('s_'),
                            f"Pattern '{pattern}' should start with 's_'")


class TestGmControllerMatcherTagPatterns(unittest.TestCase):
    """Test cases for tag pattern matching."""

    def test_get_tag_patterns_returns_list(self):
        """Test get_tag_patterns returns a list."""
        patterns = GmControllerMatcher.get_tag_patterns()

        self.assertIsInstance(patterns, list)

    def test_get_tag_patterns_not_empty(self):
        """Test get_tag_patterns returns non-empty list."""
        patterns = GmControllerMatcher.get_tag_patterns()

        self.assertGreater(len(patterns), 0)

    def test_tag_patterns_include_fifo_data_element(self):
        """Test tag patterns include z_FifoDataElement."""
        patterns = GmControllerMatcher.get_tag_patterns()

        self.assertIn('z_FifoDataElement', patterns)

    def test_tag_patterns_include_junk_data(self):
        """Test tag patterns include z_JunkData."""
        patterns = GmControllerMatcher.get_tag_patterns()

        self.assertIn('z_JunkData', patterns)

    def test_tag_patterns_include_no_data(self):
        """Test tag patterns include z_NoData."""
        patterns = GmControllerMatcher.get_tag_patterns()

        self.assertIn('z_NoData', patterns)

    def test_all_tag_patterns_are_strings(self):
        """Test all tag patterns are strings."""
        patterns = GmControllerMatcher.get_tag_patterns()

        for pattern in patterns:
            self.assertIsInstance(pattern, str)


class TestGmControllerMatcherGMNamingConventions(unittest.TestCase):
    """Test cases verifying GM-specific naming conventions."""

    def test_gm_standard_prefixes_in_patterns(self):
        """Test patterns include GM standard prefixes (zz_, sz_, cg_)."""
        module_patterns = GmControllerMatcher.get_module_patterns()

        gm_prefixes = ['zz_', 'sz_', 'cg_', 'zs_']
        for prefix in gm_prefixes:
            has_prefix = any(pattern.startswith(prefix) for pattern in module_patterns)
            self.assertTrue(has_prefix, f"Expected pattern with prefix '{prefix}'")

    def test_safety_programs_use_s_prefix(self):
        """Test safety programs use 's_' prefix convention."""
        safety_patterns = GmControllerMatcher.get_safety_program_patterns()

        for pattern in safety_patterns:
            self.assertTrue(pattern.startswith('s_'),
                            f"Safety program '{pattern}' should start with 's_'")

    def test_standard_programs_use_uppercase(self):
        """Test standard program names use uppercase."""
        program_patterns = GmControllerMatcher.get_program_patterns()

        # GM standard programs like MCP, PFE, HMI are typically uppercase
        uppercase_patterns = ['MCP', 'PFE', 'HMI1', 'HMI2', 'GROUP1', 'GROUP2']
        for pattern in uppercase_patterns:
            if pattern in program_patterns:
                self.assertEqual(pattern, pattern.upper(),
                                 f"Program pattern '{pattern}' should be uppercase")


class TestGmControllerMatcherPatternConsistency(unittest.TestCase):
    """Test cases for pattern consistency across categories."""

    def test_all_pattern_methods_return_lists(self):
        """Test all pattern getter methods return lists."""
        pattern_methods = [
            GmControllerMatcher.get_datatype_patterns,
            GmControllerMatcher.get_module_patterns,
            GmControllerMatcher.get_program_patterns,
            GmControllerMatcher.get_safety_program_patterns,
            GmControllerMatcher.get_tag_patterns
        ]

        for method in pattern_methods:
            result = method()
            self.assertIsInstance(result, list,
                                  f"{method.__name__} should return a list")

    def test_no_duplicate_patterns_in_categories(self):
        """Test each category has no duplicate patterns."""
        pattern_methods = [
            GmControllerMatcher.get_datatype_patterns,
            GmControllerMatcher.get_module_patterns,
            GmControllerMatcher.get_program_patterns,
            GmControllerMatcher.get_safety_program_patterns,
            GmControllerMatcher.get_tag_patterns
        ]

        for method in pattern_methods:
            patterns = method()
            unique_patterns = set(patterns)
            self.assertEqual(len(patterns), len(unique_patterns),
                             f"{method.__name__} contains duplicate patterns")

    def test_pattern_lists_are_non_empty(self):
        """Test all pattern lists contain at least one item."""
        pattern_methods = [
            GmControllerMatcher.get_datatype_patterns,
            GmControllerMatcher.get_module_patterns,
            GmControllerMatcher.get_program_patterns,
            GmControllerMatcher.get_safety_program_patterns,
            GmControllerMatcher.get_tag_patterns
        ]

        for method in pattern_methods:
            patterns = method()
            self.assertGreater(len(patterns), 0,
                               f"{method.__name__} should return non-empty list")


class TestGmControllerMatcherStaticMethods(unittest.TestCase):
    """Test cases for static method behavior."""

    def test_all_pattern_methods_are_static(self):
        """Test all pattern getter methods are static methods."""
        methods = [
            'get_datatype_patterns',
            'get_module_patterns',
            'get_program_patterns',
            'get_safety_program_patterns',
            'get_tag_patterns'
        ]

        for method_name in methods:
            method = getattr(GmControllerMatcher, method_name)
            # Static methods should be callable without instance
            try:
                result = method()
                self.assertIsInstance(result, list)
            except TypeError:
                self.fail(f"{method_name} should be a static method")

    def test_get_controller_constructor_is_classmethod(self):
        """Test get_controller_constructor is a class method."""
        # Should be callable without instance
        constructor = GmControllerMatcher.get_controller_constructor()
        self.assertEqual(constructor, GmController)


class TestGmControllerMatcherPatternCoverage(unittest.TestCase):
    """Test cases for comprehensive pattern coverage."""

    def test_datatype_patterns_cover_gm_standards(self):
        """Test datatype patterns cover GM standard datatypes."""
        patterns = GmControllerMatcher.get_datatype_patterns()

        expected_datatypes = ['zz_Version', 'zz_Prompt', 'zz_PFEAlarm', 'za_Toggle']
        for expected in expected_datatypes:
            self.assertIn(expected, patterns,
                          f"Missing expected datatype pattern: {expected}")

    def test_module_patterns_cover_all_gm_prefixes(self):
        """Test module patterns cover all GM prefix variants."""
        patterns = GmControllerMatcher.get_module_patterns()

        expected_prefixes = ['sz_*', 'zz_*', 'cg_*', 'zs_*']
        for expected in expected_prefixes:
            self.assertIn(expected, patterns,
                          f"Missing expected module pattern: {expected}")

    def test_program_patterns_cover_main_gm_programs(self):
        """Test program patterns cover main GM program types."""
        patterns = GmControllerMatcher.get_program_patterns()

        # Core GM programs
        core_programs = ['MCP', 'PFE']
        for program in core_programs:
            self.assertIn(program, patterns,
                          f"Missing core GM program: {program}")

    def test_safety_patterns_cover_common_and_segments(self):
        """Test safety patterns cover common program and segments."""
        patterns = GmControllerMatcher.get_safety_program_patterns()

        # Should have common safety program
        self.assertIn('s_Common', patterns)

        # Should have at least segment patterns
        has_segments = any('Segment' in p for p in patterns)
        self.assertTrue(has_segments, "Should include segment patterns")


class TestGmControllerMatcherUsageScenarios(unittest.TestCase):
    """Test cases for real-world usage scenarios."""

    def test_can_identify_gm_controller_by_mcp_program(self):
        """Test matcher can identify GM controller by MCP program presence."""
        patterns = GmControllerMatcher.get_program_patterns()

        # MCP is a strong indicator of GM controller
        self.assertIn('MCP', patterns)

    def test_can_identify_gm_controller_by_module_prefix(self):
        """Test matcher can identify GM controller by module prefixes."""
        patterns = GmControllerMatcher.get_module_patterns()

        # zz_ prefix is characteristic of GM
        has_zz_pattern = any('zz_' in p for p in patterns)
        self.assertTrue(has_zz_pattern)

    def test_can_identify_gm_controller_by_safety_common(self):
        """Test matcher can identify GM controller by s_Common program."""
        patterns = GmControllerMatcher.get_safety_program_patterns()

        # s_Common is characteristic of GM safety architecture
        self.assertIn('s_Common', patterns)


if __name__ == '__main__':
    unittest.main(verbosity=2)
