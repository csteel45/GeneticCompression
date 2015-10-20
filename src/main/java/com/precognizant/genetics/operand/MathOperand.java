/*
 * @(#)MathOperand.java $Date: Feb 15, 2011 6:28:27 PM $
 * 
 * Copyright 2011 FortMoon Consulting, Inc. All Rights Reserved.
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
package com.precognizant.genetics.operand;

import java.math.BigInteger;
import java.math.BigInteger;
import java.util.ArrayList;

import com.precognizant.genetics.node.ConstNode;
import com.precognizant.genetics.node.Node;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 * 
 * @since Jan 29, 2011 7:54:05 AM
 */
public class MathOperand implements Operand {
	private Operation operation;

	public enum Operation {
		PLUS {
			@SuppressWarnings("unchecked")
			BigInteger eval(BigInteger x, BigInteger y) {
				//System.out.println("MathOperand.add x y " + new BigInteger(x.toString()) + " " + new BigInteger(y.toString()));
				//System.out.println("MathOperand.add = " + new BigInteger(x.toString()).add(new BigInteger(y.toString())));
				return x.add(y);
			}
		},

		MINUS {
			@SuppressWarnings("unchecked")
			BigInteger eval(BigInteger x, BigInteger y) {
				return x.subtract(y);
			}
		},
		TIMES {
			@SuppressWarnings("unchecked")
			BigInteger eval(BigInteger x, BigInteger y) {
				return x.multiply(y);
			}
		},

		POWER {
			@SuppressWarnings("unchecked")
			BigInteger eval(BigInteger x, BigInteger y) {
				return x.pow(y.intValue());
			}
		},
		
		POWPOW {;
			@SuppressWarnings("unchecked")
			BigInteger eval(BigInteger x, BigInteger y) {
				BigInteger count = BigInteger.ZERO;
				//BigInteger bX = new BigInteger(x.toString());
				BigInteger bY = new BigInteger(y.toString());
				BigInteger result = BigInteger.ZERO;
				while(count.compareTo(bY) == -1) {
					count = count.add(BigInteger.ONE);
					result = result.add(new BigInteger(x.toString()).pow(y.intValue()));
					//System.out.println("Count = " + count + " bY = " + bY);
				}
				return x.pow(y.intValue());
			}
		};
		// Do arithmetic op represented by this constant
		abstract BigInteger eval(BigInteger number, BigInteger number2);
	}

	@SuppressWarnings("unused")
	private MathOperand() {
	}

	public MathOperand(Operation op) {
		this.operation = op;
	}

	@Override
	public BigInteger evaluate(ArrayList<Operation> args) {
		return this.operation.eval(args.get(0).evaluate(args), args.get(1).evaluate(args));
	}
	
	public Operation getOperation() {
		return operation;
	}

	public String toString() {
		return this.operation.toString();
	}

	public static void main(String[] args) {
		ArrayList<Node> params = new ArrayList<Node>();
		params.add(new ConstNode(2));
		params.add(new ConstNode(3));

		for (Operation op : Operation.values()) {
			//MathOperand math = new MathOperand(op);
			System.out.println("Integer Eval of 2 " + op.toString() + " 3 = " + op.eval(BigInteger.valueOf(2), BigInteger.valueOf(3)));
		}

		for (Operation op : Operation.values()) {
			MathOperand math = new MathOperand(op);
			System.out.println("Eval of 2 " + op.toString() + " 3 = " + math.evaluate(params));
		}
		
		System.out.println("Powpow 5, 20 = " + new MathOperand(Operation.POWPOW).evaluate(5, 20));

	}

	@Override
	public <T extends Node> Number evaluate(Number num1, Number num2) {
		return this.operation.eval(num1, num2);
	}

}
