def split_string(input_string):
    max_length = 4096
    if len(input_string) <= max_length:
        return [input_string]

    split_strings = []
    temp_string = ""
    code_block = False
    for line in input_string.split("\n"):
        # Check if line is a code block
        if line.strip().startswith("```"):
            code_block = not code_block

        if len(temp_string + line + "\n") > max_length and not code_block:
            split_strings.append(temp_string)
            temp_string = line + "\n"
        else:
            temp_string += line + "\n"

    if temp_string:
        split_strings.append(temp_string)

    return split_strings


from datetime import datetime


def get_current_day_str():
    return datetime.today().strftime("%Y-%m-%d")


import re


def format_to_markdown_v2(text: str):
    replacing_dict = {
        "\`": "`",
        "\*\*": "*",
    }
    for key in replacing_dict:
        text = text.replace(key, replacing_dict[key])

    # Split the text into lines
    lines = text.split("\n")

    # Process each line
    formatted_lines = []
    for line in lines:
        # Check if the line starts with "##" or "###"
        if line.startswith("##") or line.startswith("###"):
            # Remove the "##" or "###" and strip any leading or trailing spaces
            new_line = line.lstrip("#").strip()
            # Add '*' at the beginning and end of the line
            new_line = f"*{new_line}*"
            formatted_lines.append(new_line)
        else:
            # If no need to change, keep the line as it is
            formatted_lines.append(line)

    # Join the formatted lines back into a single text string
    formatted_text = "\n".join(formatted_lines)

    return formatted_text


if __name__ == "__main__":
    s = """ERC\-4337 is a significantly more complex and innovative standard compared to the ones previously discussed \(ERC\-20, ERC\-721, and ERC\-1155\)\. As of my last update in 2023, ERC\-4337, also known as Account Abstraction \(AA\), proposes a method to enable more flexible account models on Ethereum, aiming to blur the lines between externally owned accounts \(regular user wallets\) and contract accounts, enabling richer on\-chain behaviors directly from user accounts\.

The crux of ERC\-4337 lies in enabling smart contract wallets to perform actions that traditionally required externally owned accounts \(EOAs\), like initiating transactions, without the need for those accounts to hold ETH for gas or understand complex interact with dapps \(decentralized applications\)\. It introduces User Operation objects, which are bundles of instructions signed by the user and executed by Bundlers \(entities in the network that bundle these operations and submit them to the chain\)\.

It's important to note that as of the information available up to 2023, ERC\-4337 is not a token standard like ERC\-20 or ERC\-721, but rather a standard for improving account capabilities and interaction models on the Ethereum blockchain\.

Implementing ERC\-4337 or creating a smart contract wallet that leverages its functionalities would entail understanding several components:

1\. \*\*EntryPoint Contract\*\*: A standardized contract deployed to a fixed address on Ethereum that processes User Operations\.
2\. \*\*User Operation Object\*\*: A structured set of instructions including the target contract call, gas specifications, and a signature from the user's account\.
3\. \*\*Bundlers \(or Relayers\)\*\*: Participants who collect User Operations, form them into bundles, and submit them to the EntryPoint contract\.
4\. \*\*Validators\*\*: Nodes that validate these User Operations\.

Given the complexity and novelty of ERC\-4337, here's a very high\-level overview of what a component might look like, keeping in mind detailed code would be extensive and highly dependent on the specific use case:

\`\`\`solidity
// SPDX\-License\-Identifier: MIT
pragma solidity ^0\.8\.0;

// This is a very simplified representation and not a complete implementation
interface IUserOperation \{
    // Define structure or functions relevant to user operations here
\}

contract EntryPoint \{
    function handleUserOperation\(IUserOperation userOp\) external \{
        // Logic to process the user operation would go here
        // This could involve validating the operation, executing transactions, handling gas payments, etc\.
    \}
\}

// Example of a smart contract wallet leveraging ERC\-4337 Account Abstraction functionalities
contract MySmartWallet \{
    address entryPointAddress;

    constructor\(address \_entryPointAddress\) \{
        entryPointAddress \= \_entryPointAddress;
    \}

    function executeOperation\(/\* parameters defining the operation \*/\) external \{
        // Logic to create a user operation and send it to the EntryPoint
        // This part is crucial as it would define the interactions the wallet can perform
    \}
\}
\`\`\`

For a real, practical implementation, you would need to dive deeper into the specifications of ERC\-4337, potentially leveraging libraries and tools specifically designed for account abstraction\. Moreover, since the Ethereum ecosystem evolves rapidly, it’s crucial to refer to the latest documentation and discussions in the Ethereum developer community when implementing cutting\-edge standards like ERC\-4337\.

Given the complexity and potential security implications, such projects should be approached with thorough testing, potentially audits, and close attention paid to the evolving standards and implementations\."""
    print(format_to_markdown_v2(s))
