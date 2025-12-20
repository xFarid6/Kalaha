/**
 * Bitwise Operations Interactive - Main Logic
 * Educational tool for learning bitwise and binary arithmetic operations
 */

// Utility function to convert number to 8-bit binary string
function toBinary(num, bits = 8) {
    return num.toString(2).padStart(bits, '0');
}

// Tab switching
function setupTabs() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;

            // Update active states
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(`${targetTab}-tab`).classList.add('active');
        });
    });
}

// Update binary displays when inputs change
function setupInputListeners() {
    const inputA = document.getElementById('input-a');
    const inputB = document.getElementById('input-b');
    const binaryA = document.getElementById('binary-a');
    const binaryB = document.getElementById('binary-b');

    inputA.addEventListener('input', () => {
        binaryA.textContent = toBinary(parseInt(inputA.value) || 0);
    });

    inputB.addEventListener('input', () => {
        binaryB.textContent = toBinary(parseInt(inputB.value) || 0);
    });

    // Arithmetic inputs
    const arithA = document.getElementById('arith-a');
    const arithB = document.getElementById('arith-b');
    const arithBinaryA = document.getElementById('arith-binary-a');
    const arithBinaryB = document.getElementById('arith-binary-b');

    arithA.addEventListener('input', () => {
        arithBinaryA.textContent = toBinary(parseInt(arithA.value) || 0);
    });

    arithB.addEventListener('input', () => {
        arithBinaryB.textContent = toBinary(parseInt(arithB.value) || 0);
    });
}

// Create bit visualization
function createBitVisualization(label, bits, className = '') {
    const row = document.createElement('div');
    row.className = 'bit-row';

    const labelSpan = document.createElement('span');
    labelSpan.className = 'bit-label';
    labelSpan.textContent = label;
    row.appendChild(labelSpan);

    const bitsArray = bits.split('');
    bitsArray.forEach((bit, idx) => {
        const bitBox = document.createElement('div');
        bitBox.className = `bit-box ${className}`;
        bitBox.textContent = bit;
        bitBox.dataset.index = idx;
        row.appendChild(bitBox);
    });

    return row;
}

// Animate bitwise operation
async function animateBitwiseOp(a, b, operation) {
    const visualization = document.getElementById('visualization');
    visualization.innerHTML = '';

    const aBits = toBinary(a);
    const bBits = toBinary(b);

    // Create input rows
    visualization.appendChild(createBitVisualization('A:', aBits));

    if (operation !== 'not') {
        visualization.appendChild(createBitVisualization('B:', bBits));
    }

    // Operation symbol
    const opRow = document.createElement('div');
    opRow.className = 'bit-row';
    opRow.innerHTML = `<span class="operation-symbol">${getOperationSymbol(operation)}</span>`;
    visualization.appendChild(opRow);

    // Result row
    let result;
    if (operation === 'and') result = a & b;
    else if (operation === 'or') result = a | b;
    else if (operation === 'xor') result = a ^ b;
    else if (operation === 'not') result = ~a & 0xFF;
    else if (operation === 'lshift') result = (a << b) & 0xFF;
    else if (operation === 'rshift') result = a >> b;

    const resultBits = toBinary(result);
    const resultRow = createBitVisualization('Result:', resultBits, 'result');
    visualization.appendChild(resultRow);

    // Animate bit by bit
    if (operation !== 'lshift' && operation !== 'rshift') {
        for (let i = 0; i < 8; i++) {
            await animateBitOperation(i, operation);
            await delay(300);
        }
    } else {
        // For shifts, just show the result
        const resultBoxes = resultRow.querySelectorAll('.bit-box');
        resultBoxes.forEach((box, i) => {
            setTimeout(() => {
                box.classList.add('active');
            }, i * 100);
        });
    }

    return result;
}

function getOperationSymbol(op) {
    const symbols = {
        'and': 'AND (&)',
        'or': 'OR (|)',
        'xor': 'XOR (^)',
        'not': 'NOT (~)',
        'lshift': '<<',
        'rshift': '>>'
    };
    return symbols[op] || op;
}

async function animateBitOperation(bitIndex, operation) {
    const visualization = document.getElementById('visualization');
    const rows = visualization.querySelectorAll('.bit-row');
    const boxes = rows[rows.length - 1].querySelectorAll('.bit-box');

    boxes[bitIndex].classList.add('active');
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Display result
function displayResult(result) {
    const resultDiv = document.getElementById('result');
    resultDiv.classList.remove('hidden');

    resultDiv.querySelector('.result-binary').textContent = toBinary(result);
    resultDiv.querySelector('.result-decimal').textContent = `= ${result} (decimal)`;
}

// Display code
function displayCode(operation, a, b) {
    const codeDisplay = document.getElementById('code-display');
    const codeContent = document.getElementById('code-content');

    let code = '';
    if (operation === 'and') code = `const result = ${a} & ${b}; // ${a & b}`;
    else if (operation === 'or') code = `const result = ${a} | ${b}; // ${a | b}`;
    else if (operation === 'xor') code = `const result = ${a} ^ ${b}; // ${a ^ b}`;
    else if (operation === 'not') code = `const result = ~${a} & 0xFF; // ${(~a & 0xFF)}`;
    else if (operation === 'lshift') code = `const result = ${a} << ${b}; // ${(a << b) & 0xFF}`;
    else if (operation === 'rshift') code = `const result = ${a} >> ${b}; // ${a >> b}`;

    codeContent.textContent = code;
    codeDisplay.classList.remove('hidden');

    // Re-highlight code
    Prism.highlightElement(codeContent);
}

// Handle bitwise operation buttons
function setupBitwiseOperations() {
    const opButtons = document.querySelectorAll('#bitwise-tab .op-btn');

    opButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const operation = btn.dataset.op;
            const a = parseInt(document.getElementById('input-a').value) || 0;
            const b = parseInt(document.getElementById('input-b').value) || 0;

            const result = await animateBitwiseOp(a, b, operation);
            displayResult(result);
            displayCode(operation, a, b);
        });
    });
}

// Binary Arithmetic Operations
class BinaryArithmetic {
    static add(a, b) {
        const steps = [];
        let carry = 0;
        let result = 0;

        for (let i = 0; i < 8; i++) {
            const bitA = (a >> i) & 1;
            const bitB = (b >> i) & 1;
            const sum = bitA + bitB + carry;

            const resultBit = sum & 1;
            carry = sum >> 1;

            result |= (resultBit << i);

            steps.push({
                position: i,
                bitA,
                bitB,
                carry,
                resultBit,
                description: `Bit ${i}: ${bitA} + ${bitB} + carry(${carry > 0 ? 1 : 0}) = ${sum} → result=${resultBit}, carry=${carry}`
            });
        }

        return { result, steps };
    }

    static subtract(a, b) {
        // Using two's complement: a - b = a + (~b + 1)
        const steps = [];
        const complement = (~b & 0xFF) + 1;

        steps.push({
            description: `Subtract using two's complement: ${a} - ${b} = ${a} + (~${b} + 1)`,
            detail: `~${b} = ${~b & 0xFF}, then add 1 → ${complement}`
        });

        const addResult = this.add(a, complement & 0xFF);
        steps.push(...addResult.steps);

        return { result: addResult.result & 0xFF, steps };
    }

    static multiply(a, b) {
        const steps = [];
        let result = 0;

        for (let i = 0; i < 8; i++) {
            if ((b >> i) & 1) {
                const partial = a << i;
                result += partial;
                steps.push({
                    position: i,
                    description: `Bit ${i} of B is 1: Add ${a} << ${i} = ${partial & 0xFF}`,
                    partialResult: result & 0xFF
                });
            } else {
                steps.push({
                    position: i,
                    description: `Bit ${i} of B is 0: Skip`,
                    partialResult: result & 0xFF
                });
            }
        }

        return { result: result & 0xFF, steps };
    }

    static divide(a, b) {
        if (b === 0) {
            return { result: 0, steps: [{ description: 'Error: Division by zero!' }] };
        }

        const steps = [];
        let quotient = 0;
        let remainder = a;

        for (let i = 7; i >= 0; i--) {
            const divisor = b << i;
            if (remainder >= divisor) {
                remainder -= divisor;
                quotient |= (1 << i);
                steps.push({
                    position: i,
                    description: `${remainder + divisor} >= ${b} << ${i} (${divisor}): quotient bit ${i} = 1, remainder = ${remainder}`,
                    quotient,
                    remainder
                });
            } else {
                steps.push({
                    position: i,
                    description: `${remainder} < ${b} << ${i} (${divisor}): quotient bit ${i} = 0`,
                    quotient,
                    remainder
                });
            }
        }

        return { result: quotient, remainder, steps };
    }
}

// Current step tracking for arithmetic
let currentSteps = [];
let currentStepIndex = 0;

// Display algorithm steps
function displayAlgorithmSteps(steps) {
    const stepsDiv = document.getElementById('algorithm-steps');
    const stepsContent = document.getElementById('steps-content');

    currentSteps = steps;
    currentStepIndex = 0;

    stepsContent.innerHTML = '';
    steps.forEach((step, idx) => {
        const stepDiv = document.createElement('div');
        stepDiv.className = 'step';
        stepDiv.textContent = step.description || JSON.stringify(step);
        stepDiv.dataset.index = idx;
        stepsContent.appendChild(stepDiv);
    });

    stepsDiv.classList.remove('hidden');
    updateStepDisplay();
}

function updateStepDisplay() {
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, idx) => {
        step.classList.toggle('active', idx === currentStepIndex);
    });

    document.getElementById('step-counter').textContent = `Step ${currentStepIndex + 1} / ${currentSteps.length}`;
    document.getElementById('prev-step').disabled = currentStepIndex === 0;
    document.getElementById('next-step').disabled = currentStepIndex === currentSteps.length - 1;
}

// Setup arithmetic operations
function setupArithmeticOperations() {
    const opButtons = document.querySelectorAll('#arithmetic-tab .op-btn');

    opButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const operation = btn.dataset.op;
            const a = parseInt(document.getElementById('arith-a').value) || 0;
            const b = parseInt(document.getElementById('arith-b').value) || 0;

            let result;
            if (operation === 'add') result = BinaryArithmetic.add(a, b);
            else if (operation === 'sub') result = BinaryArithmetic.subtract(a, b);
            else if (operation === 'mul') result = BinaryArithmetic.multiply(a, b);
            else if (operation === 'div') result = BinaryArithmetic.divide(a, b);

            displayAlgorithmSteps(result.steps);
            displayArithmeticCode(operation, a, b, result.result);
            visualizeArithmeticOperation(operation, a, b, result);
        });
    });

    // Step navigation
    document.getElementById('prev-step').addEventListener('click', () => {
        if (currentStepIndex > 0) {
            currentStepIndex--;
            updateStepDisplay();
        }
    });

    document.getElementById('next-step').addEventListener('click', () => {
        if (currentStepIndex < currentSteps.length - 1) {
            currentStepIndex++;
            updateStepDisplay();
        }
    });
}

function visualizeArithmeticOperation(operation, a, b, result) {
    const visDiv = document.getElementById('algorithm-vis');
    visDiv.innerHTML = '';

    visDiv.appendChild(createBitVisualization('A:', toBinary(a)));
    visDiv.appendChild(createBitVisualization('B:', toBinary(b)));

    const opRow = document.createElement('div');
    opRow.className = 'bit-row';
    opRow.innerHTML = `<span class="operation-symbol">${operation.toUpperCase()}</span>`;
    visDiv.appendChild(opRow);

    visDiv.appendChild(createBitVisualization('Result:', toBinary(result.result), 'result'));
}

function displayArithmeticCode(operation, a, b, result) {
    const codeDisplay = document.getElementById('arith-code-display');
    const codeContent = document.getElementById('arith-code-content');

    let code = '';
    if (operation === 'add') {
        code = `// Binary Addition\nlet result = 0, carry = 0;\nfor (let i = 0; i < 8; i++) {\n  const bitA = (${a} >> i) & 1;\n  const bitB = (${b} >> i) & 1;\n  const sum = bitA + bitB + carry;\n  result |= ((sum & 1) << i);\n  carry = sum >> 1;\n}\n// Result: ${result}`;
    } else if (operation === 'sub') {
        code = `// Binary Subtraction (Two's Complement)\nconst complement = (~${b} + 1) & 0xFF;\nconst result = (${a} + complement) & 0xFF;\n// Result: ${result}`;
    } else if (operation === 'mul') {
        code = `// Binary Multiplication (Shift and Add)\nlet result = 0;\nfor (let i = 0; i < 8; i++) {\n  if ((${b} >> i) & 1) {\n    result += ${a} << i;\n  }\n}\n// Result: ${result & 0xFF}`;
    } else if (operation === 'div') {
        code = `// Binary Division (Shift and Subtract)\nlet quotient = 0, remainder = ${a};\nfor (let i = 7; i >= 0; i--) {\n  if (remainder >= (${b} << i)) {\n    remainder -= (${b} << i);\n    quotient |= (1 << i);\n  }\n}\n// Quotient: ${result}`;
    }

    codeContent.textContent = code;
    codeDisplay.classList.remove('hidden');
    Prism.highlightElement(codeContent);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    setupInputListeners();
    setupBitwiseOperations();
    setupArithmeticOperations();
});
