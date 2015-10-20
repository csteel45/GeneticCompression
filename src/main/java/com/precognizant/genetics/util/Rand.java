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

import java.security.SecureRandom;
import java.util.Random;

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
		System.err.println("--------------------------------------- USING SEED");
		instance.setSeed(Long.toString(System.currentTimeMillis()).getBytes());
		//Rand.instance = new Random(System.currentTimeMillis());
	}
	
	public static void init() {
		Rand.instance = new SecureRandom(Long.toString(System.currentTimeMillis()).getBytes());
	}
	
	public static int nextInt() {
		return instance.nextInt();
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

}
