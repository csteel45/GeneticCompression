/*
 * NodeTree.java
 *
 * Copyright (c) 2011-2026 Chris Steel (FortMoon Consulting, Inc.)
 * SPDX-License-Identifier: MIT
 * See the LICENSE file in the project root for the full license text.
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
