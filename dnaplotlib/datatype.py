"""
New DNAplotlib data type for designs (extendable for hierachy)
"""

__author__  = 'Thomas E. Gorochowski <tom@chofski.co.uk>'
__license__ = 'MIT'
__version__ = '2.0'


###############################################################################
# New Data Type
###############################################################################

class Part:
    def __init__(self, parent_module, name, type, orientation='+', frame=None):
        """ Constructor to generate a new Part.

        Parameters
        ----------
        parent_module : Module
            Module that this part is a member of.

        name : string
            Name of part.

        type : string
            Type of part. 

        orientation : string (default: '+')
            Orientation of the part (either '+' or '-')

        frame : (width=float, height=float, origin=float) (default: None)
            Often updated during the rendering process.
        """
        self.parent_module = parent_module
        self.name = name
        self.type = type
        self.orientation = orientation
        self.frame = frame
        self.options = {} # Options to tailor the rendering process


class PartList:
    def __init__(self, position=None, backbone='DNA'):
        """ Constructor to generate a new PartList. Used to hold a list of parts that
        should be rendered as a single unit with a shared backbone.

        Parameters
        ----------
        position : [float, float] (default: None)
            [x, y] position of the baseline start for the part. This is often updated
            during the rendering process.

        backbone : string (default: 'DNA')
            The backbone type, either DNA or RNA (will affect the rendering).
        """
        # Type of backbone (DNA or RNA, will affect rendering)
        self.position = position
        self.backbone = backbone
        self.parts = [] # List of parts making up the segment
        self.extent = [[0,0], [0,0]] # Bounding box of the part lower left to upper right coordinates.
        self.options = {} # Options to be used when rendering backbone

    def add_part(self, part):
        if type(part) != list:
            self.parts.append(part)
        else:
            self.parts += part
        


class Interaction:
    """ Constructor to generate Interaction. 

        Parameters
        ----------
        
        part_start : Part 
            specifies the start part of interaction 

        part_end : Part
            specifies the end part of interaction 

        coordinates : [[float, float]]
            specifies the list of coordinates for the interaction arrow 
            updated during rendering 

        type : string 
            Options inclue: control, degradation, inhibition, process, stimulation

        option: dict
            Options to tailor the rendering process
        """
    def __init__(self, part_start, part_end, interaction_type, path=None):
        self.part_start = part_start
        self.part_end = part_end
        self.coordinates = []
        self.type = interaction_type 
        self.path = path
        self.options = {}


class Module:
    """ Constructor to generate Module. 

        Parameters
        ----------
        
        design : Constructor 

        name : String
            name of the module

        level : Int [0, 2]
            module hierarchy level / updated during rendering

        frame : (width=float, height=float, origin=float) (default: None)
            Often updated during the rendering process.

        children : [Module]
            list of submodules contained within the module

        part_list: Part_list
            list of parts contained on dna backbone 

        other_parts: [Part]
            list of parts not contained on dna backbone 
    """
    def __init__(self, design, name, parent=None):
        self.design = design
        self.name = name
        self.level = 0 
        self.frame = None
        self.children = []
        self.part_list = None # parts on strand
        self.other_parts = [] # parts off strand

    def add_module(self, name):
        child = Module(self.design, name, parent=self)
        self.children.append(child)
        return child

    def add_part(self, part):
        if self.part_list == None:
            self.part_list = PartList()
        self.part_list.add_part(part)

    def add_other_part(self, part):
        if type(part) == list:
            self.other_parts += part
        else: self.other_parts.append(part)


class Design:
    """ Constructor to generate Module. 

        Parameters
        ----------
        name : String
            name of the module

        modules: [Module]
            list of modules contained in the design (only level 0)

        interactions: [Interactions]
            list of interactions within design
    """
    def __init__(self, name):
        self.name = name
        self.modules = []
        self.interactions = []

    def add_module(self, module):
        if type(module) != list:
            self.modules.append(module)
        else:
            self.modules += module

    def add_interaction(self, interaction):
        if type(interaction) != list:
            self.interactions.append(interaction)
        else:
            self.interactions += interaction

    def __print_part_list(self, part_list, indent=''):
        if part_list == None: return
        names = []
        for part in part_list.parts:
            names.append(part.name)
        print(indent + '  Parts: ' + ','.join(names))

    def __print_module_tree(self, starting_module, indent=''):
        # Recursive method to print tree details
        print(indent + 'Module:', starting_module.name)
        if len(starting_module.children) > 0:
            for node in starting_module.children:
                self.__print_module_tree(node, indent + '  ')
        else:
            self.__print_part_list(starting_module.part_list, indent)

    def print_design(self):
        # Generate a human-readable version of the data type
        print('Design:', self.name)
        for module in self.modules:
            self.__print_module_tree(module, indent='  ')
        for interaction in self.interactions:
            print('Interaction from part:', interaction.part_start.name, 
                  'to part:', interaction.part_end.name,
                  'of type:', interaction.type)

###############################################################################
# Testing
###############################################################################

# The basic data type at the moment works by having a Design object that holds 
# lists of the modules, interactions, and other parts making up the design. At
# the moment only the modules list is used. The other aspects will be added 
# later. The add_module method is called with a Module object to add and it will
# be appended to the list. There are also a couple private functions that the
# print_design method uses to print out the tree making up the design, drilling
# down into each module. An example of how to generate a design is shown below.
# The key detail in the datatype is that Modules can have Modules added to them 

def create_test_design ():
    # You first create a design and need to give it a name   
    design = Design('design1')
    # Create DNA module 1 (containing sub-modules)
    module1 = Module(design, 'module1')
    module1a = module1.add_module('module1a')
    part_1aCDS = Part(module1a, '1a','Promoter')
    module1a.add_part( part_1aCDS )
    module1a.add_part( Part(module1a, '1aT','Promoter') )
    module1b = module1.add_module('module1b')
    module1b.add_part( Part(module1b, '1b','Promoter') )
    module1c = module1.add_module('module1c')
    part_1cCDS = Part(module1a, '1c','Promoter')
    module1c.add_part( part_1cCDS )
    # Create DNA module 2
    module2 = Module(design, 'module2')
    part_2CDS = Part(module2, '2','Promoter')
    module2.add_part( part_2CDS )
    # Attach the different DNA segments to design
    design.add_module(module1)
    design.add_module(module2)

    # Add some other parts (e.g. molecules like a repressor)
    other_part_1Rep = Part(module2, 'R1','Unspecified')
    module2.add_other_part( other_part_1Rep )

    # Add some basic interactions
    interaction1 = Interaction(part_1cCDS, part_1aCDS, 'inhibition')
    interaction2 = Interaction(part_1cCDS, other_part_1Rep, 'process')
    interaction3 = Interaction(other_part_1Rep, part_2CDS, 'stimulation')
    design.add_interaction(interaction1)
    design.add_interaction(interaction2)
    design.add_interaction(interaction3)
    return design

def create_test_design2 ():
    # You first create a design and need to give it a name   
    design = Design('design2')

    # Create DNA module 1 
    module1 = Module(design, 'module1')
    part_1_pro = Part(module1, 'p1a','Promoter')
    part_1_res = Part(module1, 'p1r','RibosomeEntrySite') 
    part_1_cds = Part(module1, 'p1c','CDS')
    part_1_ter = Part(module1, 'p1t','Terminator')
    module1.add_part( [part_1_pro, part_1_res, part_1_cds, part_1_ter] )
    
    # Create DNA module 2
    module2 = Module(design, 'module2')
    part_2_pro = Part(module2, 'p2p','Promoter')
    part_2_cds = Part(module2, 'p2c','CDS')
    part_2_ter = Part(module2, 'p2t','Terminator')
    module2.add_part( [part_2_pro, part_2_cds, part_2_ter])

    # module 3
    module3 = Module(design, 'module3')
    part_3_pro = Part(module3, 'p3p', 'Promoter')
    part_3_ins = Part(module3, 'p3i', 'Insulator')
    part_3_ter = Part(module3, 'p3t', 'Terminator')
    module3.add_part( [part_3_pro, part_3_ins, part_3_ter] )

    # module 4
    module4 = Module(design, 'module4')
    part_4_pro = Part(module4, 'p4p', 'Promoter')
    part_4_ori = Part(module4, 'p4o', 'OriginOfReplication')
    part_4_ter = Part(module4, 'p4t', 'Terminator')
    module4.add_part( [part_4_pro, part_4_ori, part_4_ter] )

    # module 5
    module5 = Module(design, 'module5')
    part_5_pro = Part(module5, 'p5p', 'Promoter')
    part_5_ter = Part(module5, 'p5t', 'Terminator')
    module5.add_part( [part_5_pro, part_5_ter] )

    # module 6
    module6 = Module(design, 'module6')
    part_6_pro = Part(module6, 'p6a','Promoter')
    part_6_apt = Part(module6, 'p6apt', 'Aptamer')
    part_6_res = Part(module6, 'p6r','RibosomeEntrySite') 
    part_6_ter = Part(module1, 'p6t','Terminator')
    module6.add_part( [part_6_pro, part_6_apt, part_6_res, part_6_ter] )

    # module 7
    module7 = Module(design, 'module7')
    part_7_pro = Part(module7, 'p7p', 'Promoter')
    part_7_res = Part(module7, 'p7r', 'RibosomeEntrySite')
    part_7_ter = Part(module7, 'p7t', 'Terminator')
    module7.add_part( [part_7_pro, part_7_res, part_7_ter] )

    # module 8
    module8 = Module(design, 'module8')
    part_8_pro = Part(module8, 'p8p', 'Promoter')
    part_8_res = Part(module8, 'p8r', 'RibosomeEntrySite')
    part_8_ter = Part(module8, 'p8t', 'Terminator')
    module8.add_part( [part_8_pro, part_8_res, part_8_ter] )
    
    # Attach the different DNA segments to design
    design.add_module( [module1, module2, module3, module4, module5, module6, module7, module8] )

    # Add some basic interactions
    interaction1 = Interaction(part_1_cds, part_4_pro, 'control')
    int2 = Interaction(part_1_pro, part_3_pro, 'degradation')
    int3 = Interaction(part_2_cds, part_4_ori, 'process')
    int4 = Interaction(part_5_pro, part_2_pro, 'inhibition')
    int5 = Interaction(part_7_pro, part_8_res, 'stimulation')
    design.add_interaction( [interaction1, int2, int3, int4, int5] )
    return design

# hierarchical submodule rendering
def create_test_design3 ():
    # You first create a design and need to give it a name   
    design = Design('design3')

    # Create DNA module 1 
    module1 = Module(design, 'module1')
    module1a = module1.add_module('module1a')
    module1a_1 = module1a.add_module('module1a_1')
    part1a_1_p = Part(module1a_1, '1a_1_p', 'Promoter')
    module1a_1.add_part( part1a_1_p )
    module1a_1.add_part( Part(module1a_1, '1a_1_c', 'CDS'))
    module1a_1.add_part( Part(module1a_1, '1a_1_t', 'Terminator'))

    module2 = Module(design, 'module2')
    part_2_p = Part(module2, '2p', 'Promoter')
    module2.add_part(part_2_p)

    design.add_module( [module1, module2] )

    interaction = Interaction(part1a_1_p, part_2_p, 'inhibition')
    design.add_interaction(interaction)

    return design

# hierarchical submodule rendering
def create_test_design3_1 ():
    # You first create a design and need to give it a name   
    design = Design('design3')

    # Create DNA module 1 
    module1 = Module(design, 'module1')
    module1a = module1.add_module('module1a')
    module1a_1 = module1a.add_module('module1a_1')
    part1a_1_p = Part(module1a, '1a_1_p', 'Promoter')
    part1a_1_c = Part(module1a, '1a_1_c', 'CDS')
    module1a_1.add_part( [part1a_1_p, part1a_1_c ])
    module1a_1.add_part( Part(module1a_1, '1a_1_t', 'Terminator'))

    module1b = module1.add_module('module1b')
    part1b_p = Part(module1b, '1b_p', 'Promoter')
    part1b_i = Part(module1b, '1b_i', 'Insulator')
    part1b_o = Part(module1b, '1b_o', 'OriginOfReplication')
    module1b.add_part([part1b_p, part1b_i, part1b_o])

    design.add_module( module1 )

    return design

# hierarchical submodule rendering
def create_test_design3_2 ():
    # You first create a design and need to give it a name   
    design = Design('design3')

    # Create DNA module 1 
    module1 = Module(design, 'module1')
    module1a = module1.add_module('module1a')
    part1a_1_p = Part(module1, 'promoter_1a', 'Promoter')
    part1a_1_c = Part(module1, 'cds_1a', 'CDS')
    module1a.add_part( [part1a_1_p, part1a_1_c ])
    #module1a_1.add_part( Part(module1a_1, '1a_1_t', 'Terminator'))

    module1b = module1.add_module('module1b')
    part1b_p = Part(module1b, 'promoter_1b', 'Promoter')
    part1b_i = Part(module1b, 'insulator_1b', 'Insulator')
    part1b_o = Part(module1b, 'ori_1b', 'OriginOfReplication')
    module1b.add_part([part1b_p, part1b_i, part1b_o])

    design.add_module( module1 )

    return design

# hierarchical submodule rendering
def create_test_design3_3 ():
    # You first create a design and need to give it a name   
    design = Design('design3')

    # Create DNA module 1 
    module1 = Module(design, 'module1')
    module1a = module1.add_module('module1a')
    module1a_1 = module1a.add_module('module1a_1')
    part1a_1_p = Part(module1a, '1a_1_p', 'Promoter')
    part1a_1_c = Part(module1a, '1a_1_c', 'CDS')
    module1a_1.add_part( [part1a_1_p, part1a_1_c ])
    module1a_1.add_part( Part(module1a_1, '1a_1_t', 'Terminator'))

    module1b = module1.add_module('module1b')
    module1b.add_part(Part(module1b, '1b_p', 'Promoter'))

    module1c = module1.add_module('module1c')
    part1c_p = Part(module1c, '1c_p', 'Promoter')
    part1c_i = Part(module1c, '1c_i', 'Insulator')
    part1c_o = Part(module1c, '1c_o', 'OriginOfReplication')
    module1c.add_part([part1c_p, part1c_i, part1c_o])

    design.add_module( module1 )

    return design

# other part rendering
def create_test_design4 ():
    # You first create a design and need to give it a name   
    design = Design('design4')

    # Create DNA module 1 
    module1 = Module(design, 'module1')
    part_1_pro = Part(module1, '1a','Promoter')
    part_1_res1 = Part(module1, '1r1','RibosomeEntrySite') 
    part_1_res2 = Part(module1, '1r2','RibosomeEntrySite') 
    part_1_res3 = Part(module1, '1r3','RibosomeEntrySite') 
    part_1_res4 = Part(module1, '1r4','RibosomeEntrySite') 
    part_1_res5 = Part(module1, '1r5','RibosomeEntrySite') 
    part_1_cds1 = Part(module1, '1c1','CDS')
    part_1_cds2 = Part(module1, '1c2','CDS')
    part_1_cds3 = Part(module1, '1c3','CDS')
    part_1_cds4 = Part(module1, '1c4','CDS')
    part_1_ter = Part(module1, '1t','Terminator')
    # Add some other parts (e.g. molecules like a repressor)
    other_part_1Rep1 = Part(module1, 'R1','Unspecified')
    other_part_1Rep2 = Part(module1, 'R2','Macromolecule')
    other_part_1RNA = Part(module1, 'R3', 'RNA')
    module1.add_other_part( [other_part_1Rep1, other_part_1Rep2, other_part_1RNA])
    module1.add_part( [part_1_pro, part_1_res1, part_1_cds1, part_1_res2, part_1_res3, 
        part_1_cds2, part_1_res4, part_1_cds3, part_1_res5, part_1_cds4, part_1_ter] )
    
    # Create DNA module 2
    module2 = Module(design, 'module2')
    part_2_pro = Part(module2, '2p','Promoter')
    part_2_cds = Part(module2, '2c','CDS')
    part_2_ter = Part(module2, '2t','Terminator')
    module2.add_part( [part_2_pro, part_2_cds, part_2_ter])

    # module 3
    module3 = Module(design, 'module3')
    part_3_pro = Part(module3, '3p', 'Promoter')
    part_3_ins = Part(module3, '3i', 'Insulator')
    part_3_ter = Part(module3, '3t', 'Terminator')
    module3.add_part( [part_3_pro, part_3_ins, part_3_ter] )

    # module 4
    module4 = Module(design, 'module4')
    part_4_pro = Part(module4, '4p', 'Promoter')
    part_4_ori = Part(module4, '4o', 'OriginOfReplication')
    part_4_ter = Part(module4, '4t', 'Terminator')
    module4.add_part( [part_4_pro, part_4_ori, part_4_ter] )
    
    # Attach the different DNA segments to design
    design.add_module( [module1, module2, module3, module4] )

    # Add some basic interactions
    interaction1 = Interaction(part_1_cds1, part_4_pro, 'control')
    int2 = Interaction(part_1_pro, part_3_pro, 'degradation')
    int3 = Interaction(part_2_cds, part_4_ori, 'process')
    int4 = Interaction(part_2_pro, part_3_ins, 'inhibition')
    design.add_interaction( [interaction1, int2, int3, int4] )
    return design

    
def create_test_design5 ():
    # You first create a design and need to give it a name   
    design = Design('design5')

    # Create DNA module 1 
    module1 = Module(design, 'module1')
    module1.add_part( [Part(module1, 'p1p', 'Promoter'), Part(module1, 'p1c', 'CDS'), Part(module1, 'p1c2', 'CDS'), Part(module1, 'p1t', 'Terminator')])
    other_part_1p1 = Part(module1, 'R1','Unspecified')
    other_part_1p2 = Part(module1, 'R2','Macromolecule')
    other_part_1RNA1 = Part(module1, 'R5', 'RNA')
    module1.add_other_part( [other_part_1p1, other_part_1RNA1, other_part_1p2])

    # Create module 2 containing only other part 
    module2 = Module(design, 'module2')
    other_part_1 = Part(module2, 'p','Macromolecule')
    module2.add_other_part(other_part_1)

    # Create module 3 containing only other part 
    module3 = Module(design, 'module3')
    other_part_2 = Part(module3, 'rna','RNA')
    module3.add_other_part(other_part_2)

    # module 6
    module6 = Module(design, 'module6')
    part_6_pro = Part(module6, 'p6a','Promoter')
    part_6_apt = Part(module6, 'p6apt', 'Aptamer')
    part_6_res = Part(module6, 'p6r','RibosomeEntrySite') 
    part_6_ter = Part(module1, 'p6t','Terminator')
    module6.add_part( [part_6_pro, part_6_apt, part_6_res, part_6_ter] )

    # module 7
    module7 = Module(design, 'module7')
    part_7_pro = Part(module7, 'p7p', 'Promoter')
    part_7_res = Part(module7, 'p7r', 'RibosomeEntrySite')
    part_7_ter = Part(module7, 'p7t', 'Terminator')
    module7.add_part( [part_7_pro, part_7_res, part_7_ter] )

    # module 8
    module8 = Module(design, 'module8')
    part_8_pro = Part(module8, 'p8p', 'Promoter')
    part_8_cds = Part(module8, 'p8c', 'CDS')
    part_8_ter = Part(module8, 'p8t', 'Terminator')
    module8.add_part( [part_8_pro, part_8_cds, part_8_ter] )

    design.add_interaction( [Interaction(other_part_1p2, part_7_res, 'inhibition'), 
        Interaction(part_6_pro, other_part_1, 'process'),
        Interaction(part_8_cds, other_part_2, 'control')])

    design.add_module([module1, module6, module7, module8, module2, module3])

    return design


# Let's try it out!
'''
design = create_test_design5()
design.print_design()'''









