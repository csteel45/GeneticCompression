/*
 * Log.java
 *
 * Copyright (c) 2011-2026 Chris Steel (FortMoon Consulting, Inc.)
 * SPDX-License-Identifier: MIT
 * See the LICENSE file in the project root for the full license text.
 */
package com.precognizant.genetics.util;

import java.math.BigInteger;
import java.util.Random;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Aug 7, 2016 2:39:20 AM
 */
public class Log {

	private static final double LOG2 = Math.log(2.0);

	/**
	 * Computes the natural logarithm of a BigInteger. Works for really big
	 * integers (practically unlimited)
	 * 
	 * @param val Argument, positive integer
	 * @return Natural logarithm, as in <tt>Math.log()</tt>
	 */
	public static double logBigInteger(BigInteger val) {
//		if(val.bitLength() > 1023)
//			throw new ArithmeticException("Bit count too large for val. Must not exceed 1023, currentval count = " + val.bitLength());

		if(val.bitLength() < 60)
			throw new ArithmeticException("Bit count too small for val. Must be over 60.");

	    int blex = val.bitLength() - 1022; // any value in 60..1023 is ok
	    if (blex > 0)
	        val = val.shiftRight(blex);
	    double res = Math.log(val.doubleValue());
	    return blex > 0 ? res + blex * LOG2 : res;
	}
	
	public static double testLogBigInteger(int[] factors, int[] exponents) {
		double l1 = 0;
		BigInteger bi = BigInteger.ONE;
		for (int i = 0; i < factors.length; i++) {
			int exponent = exponents[i];
			int factor = factors[i];
			if (factor <= 1)
				continue;
			for (int n = 0; n < exponent; n++) {
				bi = bi.multiply(BigInteger.valueOf(factor));
			}
			l1 += Math.log(factor) * exponent;
		}
		double l2 = logBigInteger(bi);
		double err = Math.abs((l2 - l1) / l1);
		int decdigits = (int) (l1 / Math.log(10) + 0.5);
		System.out.printf("e=%e digits=%d \n", err, decdigits);
		return err;
	}
    
	/**
	 * @param args
	 */
	public static void main(String[] args) {
	    int[] f = { 1, 1, 1, 1, 1 };
	    int[] e = { 1, 1, 1, 1, 1 };
	    Random r = new Random();
	    double maxerr = 0;
	    for (int n = 0; n < 10; n++) {
	        for (int i = 0; i < f.length; i++) {
	            f[i] = r.nextInt(100000) + 2;
	            e[i] = r.nextInt(1000) + 1;
	        }
	        double err = testLogBigInteger(f, e);
	        if (err > maxerr)
	            maxerr = err;
	    }
	    System.out.printf("Max err: %e \n", maxerr);
	}

}
