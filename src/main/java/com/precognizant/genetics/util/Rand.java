/*
 * @(#)Rand.java $Date: May 25, 2011 8:32:54 PM $
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
package com.precognizant.genetics.util;

import java.math.BigInteger;
import java.security.SecureRandom;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since May 25, 2011 8:32:54 PM
 */
public class Rand {
	private static SecureRandom instance = new SecureRandom(Long.toString(System.currentTimeMillis()).getBytes());
	
	private Rand() {
	}
	
	private Rand(long seed) {
		instance = new SecureRandom(Long.toString(seed).getBytes());
	}
	
	public static void init(long seed) {
		System.out.println("--------------------------------------- USING SEED");
		instance.setSeed(Long.toString(System.currentTimeMillis()).getBytes());
		//Rand.instance = new Random(System.currentTimeMillis());
	}
	
	public static void init() {
		Rand.instance = new SecureRandom(Long.toString(System.currentTimeMillis()).getBytes());
	}
	
	public static int nextInt() {
		return Math.abs(instance.nextInt());
	}

	public static int nextInt(int top) {
		return instance.nextInt(top);
	}
	
	public static boolean nextBoolean() {
		return instance.nextBoolean();
	}
	
	public static double next() {
		return instance.nextInt(10) * 1.0;
	}

	/**
	 * @return
	 */
	public static Number nextLong() {
//		System.out.println("NextLong start");
		long rand = instance.nextInt(Integer.MAX_VALUE);
		BigInteger bi = BigInteger.valueOf(rand);
//		System.out.println("Rand1 = " + rand + "\tBS = " + bi.toString(2));
		bi = bi.shiftLeft(32);
//		System.out.println("Rand2 = " + rand + "\tBS = " + bi.toString(2));
		rand = instance.nextInt(Integer.MAX_VALUE);
		bi = bi.add(BigInteger.valueOf(rand));
//		System.out.println("Rand3 = " + rand + "\tBS = " + bi.toString(2));
//		System.out.println("NextLong end");
		return bi;
	}

}
