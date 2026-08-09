/*
 * BaseNode.java
 *
 * Copyright (c) 2011-2026 Chris Steel (FortMoon Consulting, Inc.)
 * SPDX-License-Identifier: MIT
 * See the LICENSE file in the project root for the full license text.
 */
package com.precognizant.genetics.node;

import java.math.BigDecimal;
import java.math.BigInteger;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Aug 16, 2016 9:40:57 AM
 */
public abstract class BaseNode implements Node {
	protected Number value = null;
	protected int bitLength = 0;
	protected String nodeString = null;
	public static final int LONG_LENGTH = BigInteger.valueOf(Long.MAX_VALUE).bitLength() + 1; //64

	protected BaseNode() {
		
	}	

	/**
	 * Returns the constant that this ConstNode was created with.
	 * 
	 * @see com.fortmoon.genetics.Node#evaluate(java.util.ArrayList)
	 */
	public <T extends Node> Number evaluate() {
		return value;
	}
	
	/** 
	 * Returns the bit length of the constant
	 * @see com.precognizant.genetics.node.Node#size()
	 */
	public int size() {		// LONG_LENGTH = 64
		bitLength = ((BigInteger)value).bitLength();
		if(bitLength % LONG_LENGTH == 0)
			bitLength = bitLength/LONG_LENGTH;
		else
			bitLength = (bitLength / LONG_LENGTH) + 1;

		return bitLength;
	}
	
	@Override
	public String toString() {
		if(null != nodeString) {
			return nodeString;
		}
		Number constant = evaluate();
		
		StringBuffer sb = new StringBuffer();
		if (constant instanceof Integer)
			sb.append((Integer) constant);
		else if (constant instanceof Long)
			sb.append((Long) constant);
		else if (constant instanceof Float)
			sb.append((Float) constant);
		else if (constant instanceof Double)
			sb.append((Double) constant);
		else if (constant instanceof BigDecimal)
			sb.append((BigDecimal) constant);
		else if (constant instanceof BigInteger)
			sb.append((BigInteger) constant);
		else
			sb.append("Unknown number type: " + constant);
		
		sb.append(" size = " + size());
		nodeString = sb.toString();
		return nodeString;
	}

}
