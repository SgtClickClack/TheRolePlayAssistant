/*
 * Generated by ./misc/optlib2c from optlib/terraformvariables.ctags, Don't edit this manually.
 */
#include "general.h"
#include "parse.h"
#include "routines.h"
#include "field.h"
#include "xtag.h"
#include "dependency.h"


static void initializeTerraformVariablesParser (const langType language CTAGS_ATTR_UNUSED)
{
}

extern parserDefinition* TerraformVariablesParser (void)
{
	static const char *const extensions [] = {
		"tfvars",
		NULL
	};

	static const char *const aliases [] = {
		NULL
	};

	static const char *const patterns [] = {
		NULL
	};

	static tagRegexTable TerraformVariablesTagRegexTable [] = {
		{"^([a-z0-9_]+)[[:space:]]*=", "\\1",
		"v", "{_role=assigned}{_language=Terraform}", NULL, false},
	};

	static parserDependency TerraformVariablesDependencies [] = {
		[0] = { DEPTYPE_FOREIGNER, "Terraform", NULL },
	};

	parserDefinition* const def = parserNew ("TerraformVariables");

	def->versionCurrent= 0;
	def->versionAge    = 0;
	def->enabled       = true;
	def->extensions    = extensions;
	def->patterns      = patterns;
	def->aliases       = aliases;
	def->method        = METHOD_NOT_CRAFTED|METHOD_REGEX;
	def->tagRegexTable = TerraformVariablesTagRegexTable;
	def->tagRegexCount = ARRAY_SIZE(TerraformVariablesTagRegexTable);
	def->dependencies    = TerraformVariablesDependencies;
	def->dependencyCount = ARRAY_SIZE(TerraformVariablesDependencies);
	def->initialize    = initializeTerraformVariablesParser;

	return def;
}
