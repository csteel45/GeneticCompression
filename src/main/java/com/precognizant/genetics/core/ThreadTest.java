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
