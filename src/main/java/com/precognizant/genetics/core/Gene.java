/*
 * @(#)Gene.java $Date: Feb 15, 2011 6:28:27 PM $
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
package com.precognizant.genetics.core;

import java.math.BigInteger;

import com.precognizant.genetics.node.Node;
import com.precognizant.genetics.node.NodeTreeImpl;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Feb 15, 2011 6:28:27 PM
 */
public class Gene {
	private 
	
	public Gene() {
	}
	
	public String toString() {
		return this.toString();
	}
	
	/**
	 * Used for sorting.
	 * 
	 * @see java.lang.Comparable#compareTo(java.lang.Object)
	 */
	@Override
	public int compareTo(Object o) {
		if (o instanceof Gene) {
			Gene gene = (Gene) o;
			return (this.getFitness().compareTo(c.fitness));
		}
		System.out.println("Chromosome.compareTo failed instanceof test. Exitting.");
		System.exit(-1);
		return 0;
	}
}
