import random
import math

class Connection:
    __slots__ = ('in_node', 'out_node', 'weight', 'enabled')
    def __init__(self, in_node, out_node, weight):
        self.in_node = in_node
        self.out_node = out_node
        self.weight = weight
        self.enabled = True

class Node:
    __slots__ = ('id', 'type', 'value', 'bias') # type: 0=Input, 1=Hidden, 2=Output
    def __init__(self, node_id, node_type, bias=0.0):
        self.id = node_id
        self.type = node_type
        self.value = 0.0
        self.bias = bias

class Genome:
    def __init__(self, input_count, output_count):
        self.nodes = {} # id -> Node
        self.connections = [] # list of Connection
        self.input_count = input_count
        self.output_count = output_count
        
        # Initialize Inputs (0 to input_count-1)
        for i in range(input_count):
            self.nodes[i] = Node(i, 0) # Input
            
        # Initialize Outputs (input_count to input_count+output_count-1)
        for i in range(output_count):
            idx = input_count + i
            self.nodes[idx] = Node(idx, 2) # Output

        # No initial connections? "at the beginning... networks are empty". 
        # But usually you need some connection to move. 
        # "random changes have a chance to occur". 
        # We'll rely on mutation to build it, OR start with fully connected?
        # Prompt: "at the beginning of the simulation networks are empty". Okay.
        # This implies agents will be dumb/still until they mutate connections.

    def copy(self):
        new_genome = Genome(self.input_count, self.output_count)
        # Deep copy nodes (hidden ones)
        for nid, node in self.nodes.items():
            if nid not in new_genome.nodes:
                new_genome.nodes[nid] = Node(node.id, node.type, node.bias)
        
        # Deep copy connections
        new_genome.connections = []
        for c in self.connections:
            new_c = Connection(c.in_node, c.out_node, c.weight)
            new_c.enabled = c.enabled
            new_genome.connections.append(new_c)
            
        return new_genome

    def mutate(self):
        # 1. Mutate Weights
        if random.random() < 0.8:
            for c in self.connections:
                if random.random() < 0.1:
                    c.weight += random.gauss(0, 0.5)
                    # Clamp?
                    c.weight = max(-10, min(10, c.weight))

        # 2. Add Connection
        if random.random() < 0.05:
            # Find two nodes not connected
            # Simplified: just pick random input/hidden and random output/hidden
            # Avoid cycles (feed forward only) -> ensure in_node.id < out_node.id isn't enough if arbitrary.
            # Simple DAG check: In standard NEAT, nodes have 'layers' or we sort by id if we respect topological order.
            # Let's just allow connections where source is Input/Hidden and dest is Hidden/Output?
            # And no self connections.
            
            src_keys = list(self.nodes.keys())
            dst_keys = list(self.nodes.keys())
            
            # Simple retry
            for _ in range(10):
                src_id = random.choice(src_keys)
                dst_id = random.choice(dst_keys)
                
                src = self.nodes[src_id]
                dst = self.nodes[dst_id]
                
                # Check valid flow: Input->Hidden, Input->Output, Hidden->Hidden, Hidden->Output
                # Invalid: Output->Anything, Anything->Input
                if src.type == 2: continue # Output can't be source
                if dst.type == 0: continue # Input can't be dest
                if src_id == dst_id: continue
                
                # Check exist
                exists = False
                for c in self.connections:
                    if c.in_node == src_id and c.out_node == dst_id:
                        exists = True
                        break
                if exists: continue
                
                # Create
                w = random.uniform(-1, 1)
                self.connections.append(Connection(src_id, dst_id, w))
                break

        # 3. Add Node (Bias?)
        # Standard: split a connection.
        if random.random() < 0.03:
            if not self.connections: return
            
            conn = random.choice(self.connections)
            if not conn.enabled: return
            
            conn.enabled = False
            
            # New Node
            new_id = max(self.nodes.keys()) + 1
            self.nodes[new_id] = Node(new_id, 1) # Hidden
            
            # In to New (Weight = 1)
            self.connections.append(Connection(conn.in_node, new_id, 1.0))
            # New to Out (Weight = old weight)
            self.connections.append(Connection(new_id, conn.out_node, conn.weight))

    def feed_forward(self, inputs):
        # Reset nodes
        for nid, node in self.nodes.items():
            if node.type == 0: # Input
                if nid < len(inputs):
                    node.value = inputs[nid]
            else:
                node.value = 0.0
                
            # Bias node? Prompt says "lowest neuron is the bias and is always activated".
            # Let's say Input 0 is Bias.
            if nid == 0: node.value = 1.0

        # Propagate
        # We need topological order or just iterate connections if strictly layered?
        # With arbitrary mutations, we might have weird ordering.
        # But if we only connect Input->Hidden/Out and Hidden->Hidden/Out (assuming new hid IDs > old), 
        # sorting by ID works roughly if split creates higher IDs.
        
        # To be safe for recurrent or unordered:
        # Standard Feed Forward usually assumes layers.
        # Let's simplified: Sort connections by in_node ID? No.
        # Correct way: Topological sort.
        # Lazy way for this demo: Loop connections multiple times? Or assume ID order.
        # Let's sort nodes by ID and process.
        
        sorted_nodes = sorted(self.nodes.keys())
        
        # But values need to be pushed.
        # Let's iterate nodes, for each node, sum inputs? 
        # No, connections store structure.
        
        # Let's assume ID order implies depth (Input < Hidden < Output is not guaranteed if we add hidden > output).
        # Actually NEAT usually assigns depth.
        # Hack: Since we only allow Src -> Dst, and new nodes are > old nodes,
        # We can just iterate connections if we sort them by 'in_node' dependency? No.
        
        # Real-time simulation hack: Use values from previous frame for recurrence? 
        # Or just do multiple passes.
        # For strict feedforward without cycles:
        # Calculate values for Hiddens, then Outputs.
        # Since we spawn Hiddens with High IDs, and Outputs have Low IDs (initially), this is tricky.
        # Let's just Map: Inputs, Hidden, Output.
        
        # Compute Hiddens first (if any)
        # Logic: 
        # 1. Inputs ready.
        # 2. Iterate connections. If source is Input, add to Dest.
        # 3. Apply activation to Hiddens.
        # 4. Iterate connections from Hiddens. Add to Dest.
        # 5. Apply activation to Outputs.
        
        # This requires knowing layers. 
        # Let's just do a "Relaxation" step where we process connections. 
        # If we have strict DAG, we can sort.
        # If we have cycles, we use old values.
        
        # Let's try:
        node_vals = {n: self.nodes[n].value for n in self.nodes} # Init with inputs/0
        
        # We need to process non-inputs
        # Order: Nodes sorted by ID? 
        # Inputs (0..N) -> Hiddens (>N+M) -> Outputs (N..N+M).
        # This ID scheme is messy: Outputs are low ID.
        
        # Let's just iterate connections. 
        # Limitation: Multi-hop needs multiple passes or correct order.
        # Let's do 3 passes. Enough for shallow nets.
        for _ in range(3):
            temp_vals = {n: 0.0 for n in self.nodes if self.nodes[n].type != 0}
            
            for c in self.connections:
                if c.enabled:
                    val = node_vals[c.in_node] * c.weight
                    if self.nodes[c.out_node].type != 0:
                        temp_vals[c.out_node] += val
            
            # Apply activation and update
            for nid, val in temp_vals.items():
                # Sigmoid or Tanh
                # Activation
                node_vals[nid] = math.tanh(val) # Tanh (-1 to 1)

        # Extract Outputs
        outs = []
        for i in range(self.output_count):
            idx = self.input_count + i
            outs.append(node_vals[idx])
            
        return outs
