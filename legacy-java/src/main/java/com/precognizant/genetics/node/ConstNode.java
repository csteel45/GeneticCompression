/*
 * ConstNode.java
 *
 * Copyright (c) 2011-2026 Chris Steel (FortMoon Consulting, Inc.)
 * SPDX-License-Identifier: MIT
 * See the LICENSE file in the project root for the full license text.
 */
package com.precognizant.genetics.node;

import java.math.BigInteger;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 * 
 * @since Jan 29, 2011 2:22:40 AM
 */
public class ConstNode extends BaseNode {

	/**
	 * Creates a ConstNode with constant set to number.
	 * 
	 * @param number The number that represents the constant.
	 */
	public ConstNode(Number number) {
		this.value = number;
		nodeString = toString();
	}
	
	public static void main(String[] args) {
		BigInteger bi = new BigInteger("18446744073709551615");
		Node cn = new ConstNode(bi);
		System.out.println("64bit BI = " + cn);
		bi = new BigInteger("18446744073709551616");
		cn = new ConstNode(bi);
		System.out.println("65bit BI = " + cn);
		System.out.println("Max long =  " + Long.MAX_VALUE);
	}

}
