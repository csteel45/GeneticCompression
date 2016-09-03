/*
 * @(#)ConstNode.java $Date: Feb 15, 2011 6:28:27 PM $
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
