/*
 * @(#)Population.java $Date: Feb 15, 2011 6:28:27 PM $
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

import java.io.Serializable;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;

import com.precognizant.genetics.data.TestData;
import com.precognizant.genetics.node.ConstNode;
import com.precognizant.genetics.node.FunctionNodeBase;
import com.precognizant.genetics.node.Node;
import com.precognizant.genetics.node.ParamNode;
import com.precognizant.genetics.operand.MathOperand;
import com.precognizant.genetics.operand.Operand;
import com.precognizant.genetics.util.Rand;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 * 
 * @since Feb 15, 2011 6:28:27 PM
 */
public class Population implements Serializable {
	// protected TestData testData;
	protected ArrayList<TestData> testSet;
	protected Double mutationRate = 0.4;
	private static final long serialVersionUID = 1L;
	private static final BigInteger ZERO = BigInteger.valueOf(0);
	private ArrayList<Chromosome> chromosomes;
	private int inputSize;
	private int sizeMutationRate = 10 * 48; // Need to factor in number of chromosomes
	public long mutations = 0;
	private boolean elitism = true;
	private BigInteger populationFitness = BigInteger.valueOf(Long.MAX_VALUE);
	private long generation = 0;

	private Population() {
		chromosomes = new ArrayList<Chromosome>();
	}

	public Population(int numChromosomes, int numVariables) {
		this();
		this.inputSize = numVariables;
		this.setNumChromosomes(numChromosomes);
	}

	/**
	 * Calculates the fitness of the Population, with zero being best and higher
	 * numbers representing less fit populations.
	 * 
	 * @return BigInteger representation of fitness with 0.0 being fittest
	 */
	public BigInteger calculateFitness() {
		
		BigInteger fitness = ZERO;
		for (Chromosome c : chromosomes) {
			fitness = c.calculateFitness(this.getTestData(this.testSet));
			if(fitness.compareTo(populationFitness) < 0) {
				System.out.println("Setting population fitness " + populationFitness + " to: " + fitness);
				populationFitness = fitness;
			}
		}
		sort(); // Sort the chromosomes based on fitness
		
		populationFitness = chromosomes.get(0).getFitness();
		return populationFitness;
	}
	
	public void evolve() {
		doCrossovers();
		calculateFitness();
		doMutations();
		calculateFitness();
		if(generation % 1000 == 1) {
			System.out.println("Fittest = " + getFittest().toString());
			//this.refactorFittest();
			//System.out.println("Refactored Fittest = " + population.getFittest().toString());
			System.out.println("Generations = " + generation + " Gene Additions = " + mutations);
		}
		generation++;

	}

	/**
	 * Performs a cross-over of Genes between Chromosomes in the Population.
	 * 
	 */
	public void doCrossovers() {
		Chromosome source = chromosomes.get(0);
		for (int i = 0; i < chromosomes.size()-1; i++) { // Iterate through all but least fit
			// Grab random genes
			int geneIndex = Rand.nextInt(source.getGenes().size());
			Gene gene = source.getGenes().get(geneIndex);
			Chromosome target = chromosomes.get(i);

			if (target.getGenes().size() >= geneIndex + 1)
				target.getGenes().set(geneIndex, gene);
			else
				target.getGenes().add(gene);
			
			if(isElitism())
				source = chromosomes.get(i + 1); // pass crossover genes down
			else
				source = chromosomes.get(Rand.nextInt(chromosomes.size()-1)+1); // randomly crossover except to fittest
		}
	}

	public void doMutations() {
		// Let's mutate a viable percentage of the population
		int numMutations = (int) (chromosomes.size() * mutationRate);
		// System.out.println("Num mutations = " + numMutations);
		for (int i = 0; i < numMutations; i++) {
			// Grab a random Chromosome but don't mutate the fittest
			Chromosome c = chromosomes.get(Rand.nextInt(chromosomes.size() - 1) + 1);
			// Change a gene
			c.mutate();
			// Very infrequently, add a gene
			if (Rand.nextInt(sizeMutationRate) == 1) {
				mutations++;
				//System.out.println("Adding a gene. Length = " + (c.getGenes().size() + 1));
				Gene newGene = new Gene(this.testSet.get(0).getInputs().size());
				c.getGenes().add(newGene);
				// System.out.println("adding new Gene: " + newGene);
			}
			// Or remove a gene  1/sizeMutationRate (i.e.1/10000)
			if (Rand.nextInt(sizeMutationRate) == 1) {
				if (c.getGenes().size() > 1) {
					// System.out.println("Removing a gene.");
					c.getGenes().remove(Rand.nextInt(c.getGenes().size()));
				}
			}
		}
	}

	public Chromosome getFittest() {
		sort(); // FIXME We already do a sort during calculateFitness. Can we skip it here?
		return chromosomes.get(0);
	}
	
	public void sort() {
		//System.out.println("Sort called");
		Collections.sort(chromosomes);
		//System.out.println("Most fit: " + chromosomes.get(0) + "\nLeast fit: " + chromosomes.get(chromosomes.size() - 1));
	}

	public int getNumChromosomes() {
		return chromosomes.size();
	}

	public void setNumChromosomes(int numChromosomes) {
		if (numChromosomes == chromosomes.size())
			return;

		if (chromosomes.size() < numChromosomes) {
			int diff = numChromosomes - chromosomes.size();
			for (int i = 0; i < diff; i++) {
				// Start with 1 gene per Chromosome and grow
				Chromosome c = new Chromosome(1, inputSize);
				c.setFitness(BigInteger.valueOf(Integer.MAX_VALUE));
				chromosomes.add(c);
			}
		} 
		else {
			int diff = chromosomes.size() - numChromosomes;
			for (int i = 0; i < diff; i++) {
				chromosomes.remove(chromosomes.size() - 1);
			}
		}
		System.out.println("Population size now = " + chromosomes.size());
	}

	public ArrayList<TestData> getTestData() {
		return testSet;
	}

	public void setTestData(ArrayList<TestData> testSet) {
		System.out.println("Setting test data.");
		this.testSet = testSet;
	}

	public Double getMutationRate() {
		return mutationRate;
	}

	public void setMutationRate(Double mutationRate) {
		this.mutationRate = mutationRate;
	}
	
	/**
	 * @return the useElitism
	 */
	public boolean isElitism() {
		return elitism;
	}

	/**
	 * @param useElitism the useElitism to set
	 */
	public void setElitism(boolean elitism) {
		this.elitism = elitism;
	}

	private void addChromosome(Chromosome c) {
		this.chromosomes.add(c);
	}

	public static void main(String[] args) {
		int generation = 0;
		int testSize = 1;
		int numVariables = 2;

		Population population = new Population(48, numVariables);
		ArrayList<TestData> testData = new ArrayList<TestData>(testSize);

		for (int i = 0; i < testSize; i++) {
			ArrayList<BigInteger> set = new ArrayList<BigInteger>(numVariables);

			BigInteger x = BigInteger.valueOf(Rand.nextInt(49) + 1);
			BigInteger y = BigInteger.valueOf(Rand.nextInt(49) + 1);
			BigInteger z = BigInteger.valueOf(Rand.nextInt(49) + 1);

			// double result = ((x/y) + 2.0 + (x * 9) + (z * 3));
			double xd = x.doubleValue();
			double yd = y.doubleValue();
			double zd = z.doubleValue();
			System.out.println("x = " + xd);
			System.out.println("y = " + yd);
			System.out.println("x * 9 = " + (xd * 9.0));
			long result = (long) ((2 * zd) + (xd * 9) + (yd / xd));
			// BigInteger result = y.divide(BigInteger.valueOf(1), 1,
			// DOWN).add(BigInteger.valueOf(2)).add(x.multiply(BigInteger.valueOf(9))).add(z.multiply(BigInteger.valueOf(3)));
			System.out.println("Result: " + result);
			set.add(x);
			set.add(y);
			set.add(z);
			TestData datum = new TestData(set, BigInteger.valueOf(result));
			testData.add(datum);
			population.testSet = testData;
		}

		System.out.println("Test data = " + testData);
		population.setTestData(testData);

		//System.out.println("Fittest = " + population.getFittest().toString());
		System.out.println("Generations = " + generation + " Gene additions = " + population.mutations);

		Chromosome c = new Chromosome(2);
		ArrayList<Gene> genes = new ArrayList<Gene>();
		ArrayList<Node> params = new ArrayList<Node>();

		ParamNode xNode = new ParamNode(0);
		ParamNode yNode = new ParamNode(1);
		ParamNode zNode = new ParamNode(2);
		
		params.add(yNode);
		params.add(xNode);
		Operand op = new MathOperand(MathOperand.Operation.DIVIDE);
		Node node = new FunctionNodeBase(op, params);
		Gene xDivYgene = new Gene(node);

		Operand op2 = new MathOperand(MathOperand.Operation.TIMES);
		ArrayList<Node> params2 = new ArrayList<Node>();
		params2.add(new ConstNode(BigInteger.valueOf(2)));
		params2.add(zNode);
		Node node2 = new FunctionNodeBase(op2, params2);
		Gene twogene = new Gene(node2);

		op = new MathOperand(MathOperand.Operation.TIMES);
		params = new ArrayList<Node>();
		params.add(xNode);
		params.add(new ConstNode(BigInteger.valueOf(9)));
		node = new FunctionNodeBase(op, params);
		Gene nineXgene = new Gene(node);

		genes.add(xDivYgene);
		genes.add(twogene);
		genes.add(nineXgene);
		c.setGenes(genes);
		population.chromosomes.set(18, c);
		population.calculateFitness();
		population.sort();

//		System.out.println("Fitness of Perfect Chromosome = " + population.calculateChromosomeFitness(c) + " " + c);
		System.out.println("Most fit: " + population.chromosomes.get(0) + "\nLeast fit: " + population.chromosomes.get(population.chromosomes.size() - 1));

		//generation++;
		// population.doCrossovers();
		// population.sort();
		// population.doMutations();
		//population.sort();

	}

}
