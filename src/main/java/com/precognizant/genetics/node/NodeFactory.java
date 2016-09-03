/*
 * @(#)NodeFactory.java $Date: Aug 6, 2016 9:45:29 PM $
 * 
 * Copyright © 2016 FortMoon Consulting, Inc. All Rights Reserved.
 * 
 * This software is the confidential and proprietary information of FortMoon
 * Consulting, Inc. ("Confidential Information"). You shall not disclose such
 * Confidential Information and shall use it only in accordance with the terms
 * of the license agreement you entered into with FortMoon Consulting.
 * 
 * FORTMOON MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
 * SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR
 * NON-INFRINGEMENT. FORTMOON SHALL NOT BE LIABLE FOR ANY DAMAGES SUFFERED BY
 * LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS
 * DERIVATIVES.
 * 
 */
package com.precognizant.genetics.node;

import java.util.ArrayList;

import com.precognizant.genetics.operand.MathOperand;
import com.precognizant.genetics.operand.MathOperand.Operation;
import com.precognizant.genetics.operand.Operand;
import com.precognizant.genetics.util.Rand;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Aug 6, 2016 9:45:29 PM
 */
public class NodeFactory {
	static ArrayList<Operand> operandList = new ArrayList<Operand>();
	
	static {
		// operandList.add(new IfOperand());
		operandList.add(new MathOperand(Operation.PLUS));
//		operandList.add(new MathOperand(Operation.MINUS));
		operandList.add(new MathOperand(Operation.TIMES));
		operandList.add(new MathOperand(Operation.POWER));
//		operandList.add(new MathOperand(Operation.POWPOW));
		//operandList.add(new IfOperand());
	}
	
	/**
	 * Return a random Const or Function Node
	 */
	public static Node getRandomNode() {
		Node node = null;
		if(Rand.nextBoolean())
			node = NodeFactory.getRandomFunctionNode();
		else
			node = NodeFactory.getRandomConstNode();
		
		return node;
	}
	
	/**
	 * Return a Random Operand.
	 */
	public static Operand getRandomOperand() {
		return operandList.get(Rand.nextInt(operandList.size()));
	}

	/**
	 * Return a random Const node.
	 */
	public static Node getRandomConstNode() {
		return new ConstNode(Rand.nextLong());
	}

	/**
	 * Return a random FunctionNode.
	 */
	public static Node getRandomFunctionNode() {
		Node node = null;
		node = new FunctionNode(getRandomConstNode(), getRandomOperand(), getRandomConstNode());

		return node;
	}
	
	public static void main(String[] args) {
		for(int i = 0; i < 100; i++) {
			Node node =  getRandomNode();
			System.out.println("[Random node] = " + node);
		}
	}

}
