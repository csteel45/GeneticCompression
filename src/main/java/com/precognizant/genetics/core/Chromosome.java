/*
 * @(#)Chromosome.java $Date: Feb 15, 2011 6:28:27 PM $
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
import java.util.ArrayList;
import java.util.Collections;
import java.util.UUID;

import com.precognizant.genetics.util.Rand;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Feb 15, 2011 6:28:27 PM
 */
public class Chromosome implements Runnable, Comparable<Object> {
	private ArrayList<Gene> genes;
	private BigInteger fitness = BigInteger.ZERO;
	private UUID uuid;
	private BigInteger goal = null;

	private Chromosome() {
		uuid = UUID.randomUUID();
	}
	
	public Chromosome(int numGenes, BigInteger goal) {
		this();
		this.goal = goal;
		genes = new ArrayList<Gene>(numGenes);
		for (int i = 0; i < numGenes; i++) {
			genes.add(createGene());
		}
		this.getFitness();
	}

	private Gene createGene() {
		//FIXME: Complete.
		return null;
	}

	public void mutate() {
		//FIXME: Change to mutate at same scale???
		Gene mutation = createGene();
		genes.set(Rand.nextInt(genes.size()), mutation);
	}

	public int getNumGenes() {
		return genes.size();
	}

	public void setGenes(ArrayList<Gene> genes) {
		this.genes = genes;
	}

	public ArrayList<Gene> getGenes() {
		return genes;
	}

	public BigInteger getFitness() {
		BigInteger result = BigInteger.ZERO;
		for(Gene gene : genes) {
			result = result.add(gene.evaluate());
			//System.out.println("Gene " + gene + " Result for " + x + " " + y + " = " + result);
		}
		fitness = goal.subtract(result).abs();
		return fitness;
	}

	/* (non-Javadoc)
	 * @see java.lang.Runnable#run()
	 */
	@Override
	public void run() {
		eval();
	}

	/**
	 * Used for sorting.
	 * 
	 * @see java.lang.Comparable#compareTo(java.lang.Object)
	 */
	@Override
	public int compareTo(Object o) {
		if (o instanceof Chromosome) {
			Chromosome c = (Chromosome) o;
			return (this.getFitness().compareTo(c.fitness));
		}
		System.out.println("Chromosome.compareTo failed instanceof test. Exitting.");
		System.exit(-1);
		return 0;
	}
	
	public String toString() {
		StringBuffer buf = new StringBuffer();
		buf.append("\n\tUUID: " + uuid);
		buf.append("\n\tFitness: " + fitness);
		for (Gene gene : genes) {
			buf.append("\n\tGene: " + gene);
		}
		return buf.toString();
	}

	public static void main(String[] args) {
		ArrayList<Chromosome> list = new ArrayList<Chromosome>();
		for (int i = 0; i < 48; i++) {
			Chromosome c = new Chromosome(4, BigInteger.valueOf(13l * i));
			list.add(c);
		}
		// System.out.println("Unsorted list: " + list);
		Collections.sort(list);
		System.out.println("Sorted list: " + list);

	}

}
