/*
 * @(#)ThreadTest.java $Date: Oct 19, 2015 8:51:13 PM $
 * 
 * Copyright © 2015 FortMoon Consulting, Inc. All Rights Reserved.
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
package com.precognizant.genetics.core;

import java.math.BigDecimal;
import java.math.BigInteger;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Oct 19, 2015 8:51:13 PM
 */
public class ThreadTest {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		
		BigInteger big = new BigInteger("87123648912734619831");
		long longNum = big.longValue();
		System.out.println("Big value =   " + big);
		System.out.println("Long value = " + longNum);
		System.out.println("Long Max   = " + Long.MIN_VALUE);
		System.out.println("Big compares to long max: " + big.compareTo(BigInteger.valueOf(Long.MAX_VALUE)));
		
		String test = new String("Mary had a little lamb");
		byte[] buf = test.getBytes();
		byte[] rev = new byte[buf.length];
		for(int i = 0; i < buf.length; i++) {
			rev[(buf.length-1) - i] = buf[i];
		}
		String reverse = new String(rev);
		System.out.println("Reverse String = " + reverse);
		
		
		
		
		
		
		
		
		
		
		
		
		for(int i = 0; i < 3; i++) {
			Thread t = new Thread(new Runnable() {
				public void run() {
					for(int j = 0; j < 1000000; j++) {
						BigDecimal result = BigDecimal.valueOf(j).pow(j);
					}
				}
			});
			t.start();
		}

	}

}
