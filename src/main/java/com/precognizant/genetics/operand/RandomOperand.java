/*
 * @(#)IfOperand.java $Date: Feb 15, 2011 6:28:27 PM $
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

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.math.BigDecimal;
import java.security.SecureRandom;
import java.util.ArrayList;

import com.precognizant.genetics.node.FunctionNode;
import com.precognizant.genetics.node.Node;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 * 
 * @since Jan 29, 2011 7:54:05 AM
 */
public class RandomOperand implements Operand {
	protected static ArrayList<Method> operations = new ArrayList<Method>();
	private static SecureRandom random = new SecureRandom();
	
	static {
		buildOperandList();
	}

	public <T extends Node> Number evaluate(ArrayList<T> args) {
		System.out.println("Evaluate(args) called");
		if(args.size() < 3)
			throw new RuntimeException("Invalid number of arguments. Must be at least 3.");
		if(!(args.get(0) instanceof FunctionNode))
			throw new RuntimeException("First argument must be a FunctionNode.");
//		if (args.get(0).evaluate(args).doubleValue() > 0) {
			return args.get(1).evaluate(args);
//		} 
/*		else {
			System.out.println("*********** args0.evaulate !> 0");
			return args.get(2).evaluate(args);
		}
*/	}
	
	private static void buildOperandList() {
//		Class<Math> mathClass = Math.class;
		Class<BigDecimal> mathClass = BigDecimal.class;
		for(Method m : mathClass.getMethods()) {
			boolean add = true;
			//  System.out.println("\nInspecting method: " + m.getName());
			Class<?>[] params = m.getParameterTypes();
			if(params.length != 1)
				add = false;
			else 
				for(Class<?> c : params) {
					//System.out.println("\tParam class: " + c.getName());
					if(c.getName() != mathClass.getName())
						add = false;
				}
			if(add)
				operations.add(m);
		}

		//System.out.println("\nFound good methods: ");
		for(Method m : operations) {
			System.out.println("\t" + m.getName());
		}
	}
	
	public Method getRandomOperation() throws IllegalArgumentException, IllegalAccessException, InvocationTargetException {
		return this.operations.get(random.nextInt(operations.size()));
	}

	public void testRandomOperation() throws IllegalArgumentException, IllegalAccessException, InvocationTargetException {
		BigDecimal num = new BigDecimal(5.0d);
		for (Method m : operations) {
			System.out.println ("5 " + m.getName() + " 2 = " + m.invoke(num, new BigDecimal(2)));
		}
	}

	public static void main(String[] args) {
//		Integer two = new Integer(2);
//		for (int i = 0; i < 10; i++) {
			RandomOperand op = new RandomOperand();
			try {
				op.testRandomOperation();
				for(int i = 0; i < 40; i++) {
					System.out.println("Random operand: " + op.getRandomOperation());
				}
			} 
			catch (IllegalArgumentException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} 
			catch (IllegalAccessException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} 
			catch (InvocationTargetException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
//			System.out.println("if(" + i + ", 3) = " + op.evaluate(i, 3));
//		}
	}

	@Override
	public <T extends Node> Number evaluate(Number num1, Number num2) {
		// TODO Auto-generated method stub
		return null;
	}

}
