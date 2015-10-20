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
			<T extends Number> T eval(T x, T y) {
				//System.out.println("MathOperand.add x y " + new BigInteger(x.toString()) + " " + new BigInteger(y.toString()));
				//System.out.println("MathOperand.add = " + new BigInteger(x.toString()).add(new BigInteger(y.toString())));
				return (T) new BigInteger(x.toString()).add(new BigInteger(y.toString()));
			}
		},

		MINUS {
			@SuppressWarnings("unchecked")
			<T extends Number> T eval(T x, T y) {
				return (T) new BigInteger(x.toString()).subtract(new BigInteger(y.toString()));
			}
		},
		TIMES {
			@SuppressWarnings("unchecked")
			<T extends Number> T eval(T x, T y) {
				return (T) new BigInteger(x.toString()).multiply(new BigInteger(y.toString()));
			}
		},

		DIVIDE {
			@SuppressWarnings("unchecked")
			<T extends Number> BigInteger eval(T x, T y) {
				BigInteger X = BigInteger.valueOf(x.longValue());
				BigInteger Y = BigInteger.valueOf(y.longValue());

				if (y.equals(BigInteger.valueOf(0)))
					return (BigInteger) Y;
				try {
					if (x instanceof Integer || x instanceof Long)
						return X.divide(Y);
					else {
						//System.out.println("Dividing without rounding");
						return X.divide(Y);
						//return (T) X.divide(Y, 10, BigInteger.ROUND_DOWN);
					}
					// return (T) X.divide(Y, 10, BigInteger.ROUND_DOWN);
				} catch (Exception e) {
					return (BigInteger) BigInteger.valueOf(0);
				}
			}
		},

		POWER {
			@SuppressWarnings("unchecked")
			<T extends Number> T eval(T x, T y) {
				return (T) new BigInteger(x.toString()).pow(new BigInteger(y.toString()).intValue());
			}
		},
		
		POWPOW {;
			@SuppressWarnings("unchecked")
			<T extends Number> T eval(T x, T y) {
				BigInteger count = BigInteger.ZERO;
				//BigInteger bX = new BigInteger(x.toString());
				BigInteger bY = new BigInteger(y.toString());
				BigInteger result = BigInteger.ZERO;
				while(count.compareTo(bY) == -1) {
					count = count.add(BigInteger.ONE);
					result = result.add(result.pow(x.intValue()));
					//System.out.println("Count = " + count + " bY = " + bY);
				}
				return (T) new BigInteger(x.toString()).pow(new BigInteger(y.toString()).intValue());
			}
		};
		// Do arithmetic op represented by this constant
		abstract <T extends Number> Number eval(T number, T number2);
	}

	@SuppressWarnings("unused")
	private MathOperand() {
	}

	public MathOperand(Operation op) {
		this.operation = op;
	}

	@Override
	public <T extends Node> Number evaluate(ArrayList<T> args) {
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
			//MathOperand math = new MathOperand(op);
			System.out.println("Float Eval of 2 " + op.toString() + " 3.1 = " + op.eval(new Float(2), new Float(3.1)));
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
