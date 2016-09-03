/*
 * @(#)NodeTree.java $Date: Feb 15, 2011 6:28:27 PM $
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
package com.precognizant.genetics.node;

import java.math.BigDecimal;
import java.math.BigInteger;

import com.precognizant.genetics.util.Log;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 * 
 * @since Jan 29, 2011 8:58:43 AM
 */
public class NodeTree {

	public NodeTree() {
	}

	public Node buildTree(BigInteger target) {
		Node rootNode = NodeFactory.getRandomFunctionNode();
		return rootNode;
	}

	public static void main(String[] args) {
		System.out.println("Long MAX = " + Long.MAX_VALUE);
		BigInteger num = new BigInteger("65535");
		//BigInteger num = BigInteger.valueOf(Long.MAX_VALUE);
		System.out.println("Num size = " + num.bitLength());
		BigInteger num2 = new BigInteger("65536");
		double d = Log.logBigInteger(num2.pow(10));
		System.out.println("Num2 bit length = " + num2.bitLength());
		System.out.println("Num2 bit count = " + num2.bitCount());
		System.out.println("Log of big num = " + d);
		BigInteger num3 = BigInteger.valueOf(2).pow((int) d);
		System.out.println("Pow of big num = " + num3);
		System.out.println("Diff = " + num2.subtract(num3));
	}

}
