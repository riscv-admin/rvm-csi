import textwrap, pathlib

def format_c_comment_lines(input_string):
    out_str = ""
    for lines in textwrap.wrap(input_string,80):
        out_str += ("* " + lines).rstrip() + "\n "
    return out_str

def format_c_comment_lines_from_array(input_array):
    out_str = ""
    for item in input_array:
        out_str += format_c_comment_lines(item)
        out_str += "*\n "
    return out_str    

def format_c_include_file(include_file):
    out_str = ""
    if (include_file['system-header']):
        out_str += "#include <" + include_file['filename'] + ">\n"   
    else:
        out_str += "#include \"" + include_file['filename'] + "\"\n"
    return out_str    

def format_c_type_prefix_list(prefix_list):
    # values can be ["const", "static", "volatile", "inline"]
    # order is important for C compilation
    out_str = ""
    if "static" in prefix_list:
        out_str += "static "
        
    if "volatile" in prefix_list:
        out_str += "volatile "
        
    if "inline" in prefix_list:
        out_str += "inline "        

    if "const" in prefix_list:
        out_str += "const "
        
    return out_str
    
def format_c_type_declaration(declaration):
    def indent():
        return "    "   # indent 4 spaces 
    
    out_str = ""
     
    # values can be "struct", "enum", "int", "unsigned"
    c_type = declaration['type']
    if c_type == "int":
        out_str += "typedef int " + declaration['name'] + ";\n"
        
    elif c_type == "unsigned":
        out_str += "typedef unsigned int " + declaration['name'] + ";\n"
        
    elif c_type == "enum":
        out_str += "typedef enum {\n"
        for member in declaration['enum-members']:
            out_str += indent() + member['name'] 
            if 'value' in member.keys():
                out_str += " = " + str(member['value']) 
            out_str += ",\n" # trailing comma should be valid for modern compilers
        out_str += "} " + declaration['name'] + ";\n"
            
    elif c_type == "struct":
        out_str += "typedef struct {\n"
        for member in declaration['struct-members']:
            member_type = member['type']
            delimiter = " "
            if member_type[-1] == '*': # pointer
                delimiter = ""
            
            out_str += indent() + member_type + delimiter + member['name'] + ";\n"
        out_str += "} " + declaration['name'] + ";\n"
        
    else:
        raise('undefined C type definition')   # Should not be possible to reach here            
    
    # TODO does it make sense to have prefixes with typedefs ??
    #if 'type-prefixes' in declaration.keys():
    #    out_str = format_c_type_prefix_list(declaration['type-prefixes']) + out_str
                     
    return out_str

def format_c_function(function):
    # Start the comment.
    out_str = "/*\n "
        
    out_str += format_c_comment_lines(function['description'])
            
    # Close comment
    out_str += "*/\n"
    
    return_type = "void" 
    if 'c-return-type' in function.keys():
        return_type = function['c-return-type']['type']
    
    out_str += return_type + " " + function['name'] + "("
    if 'c-params' in function.keys():
        for param in function['c-params']:
            
            param_type = param['type']
            delimiter = " "
            if param_type[-1] == '*': # pointer
                delimiter = ""
                    
            out_str += param_type + delimiter + param['name'] + ", "
        
        out_str = out_str.rstrip(", ") # Get rid of last comma/space
        
    else:
        out_str += "void"       
    
    out_str +=");\n"
    return out_str     

def generate_c(api_definition, out_dir):
    for module in api_definition['modules']:
        
        out_file = pathlib.Path(out_dir, module['c-filename'])
        
        # Start the comment.
        out_str = "/*\n "
        
        # Insert the module name,  description & boilerplate strings line per line
        out_str += format_c_comment_lines(module['name'])
        out_str += "*\n "
        
        out_str += format_c_comment_lines(module['description'])
        out_str += "*\n "
        
        out_str += format_c_comment_lines(api_definition['boilerplate'])

        # Close comment
        out_str += "*/\n\n"

        # Guard against multiple inclusion with define based on filename, e.g. csi_defs.h => CSI_DEFS_H 
        def_file_name = pathlib.Path(out_file).name.upper().replace('.','_')
        out_str += "#ifndef " + def_file_name + "\n"
        out_str += "#define " + def_file_name + "\n"
        
        out_str += "\n"
        
        # Add include files        
        if 'c-include-files' in module.keys():
            for include_file in module['c-include-files']:
                out_str += format_c_include_file(include_file)
            out_str += "\n"
                    
        # Add type declarations
        if 'c-type-declarations' in module.keys():
            for type_declaration in module['c-type-declarations']:
                out_str += format_c_type_declaration(type_declaration)
                out_str += "\n"
            out_str += "\n"
            
        # Add function declarations
        if 'functions' in module.keys():
            for function in module['functions']:
                out_str += format_c_function(function)
                out_str += "\n"
            out_str += "\n"        
                
        # Close guard against multiple inclusion
        out_str += "#endif /* " + def_file_name + " */ \n"
        
        # Write to the output file
        out_file.parent.mkdir(exist_ok=True, parents=True)
        out_file.write_text(out_str)