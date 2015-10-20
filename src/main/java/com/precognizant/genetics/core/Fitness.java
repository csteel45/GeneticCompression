/*
 * Copyright 2014 Software AG Government Solutions
 * All Rights Reserved.
 *
 * This software is the confidential and proprietary information of Softwre AG
 * Government Solutions ("Confidential Information").  You shall not
 * disclose such Confidential Information and shall use it only in
 * accordance with the terms of the license agreement you entered into
 * with Software AG Government Soltuions.
 *
 * SOFTWARE AG GS MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
 * SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
 * PURPOSE, OR NON-INFRINGEMENT. SOFTWARE AG GS SHALL NOT BE LIABLE FOR ANY DAMAGES
 * SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
 * THIS SOFTWARE OR ITS DERIVATIVES.
 */

package com.precognizant.genetics.core;

import java.io.Serializable;
import java.math.BigDecimal;

/**
 * @author Christopher Steel - Software AG Government Solutions
 *
 * @since Oct 1, 2014 11:56:12 AM
 * @version 1.0
 */
public interface Fitness extends Serializable {
	
	/**
	 * Evaluates the fitness of an individual chromosome.
	 * 
	 * @param chromosome The chromosome to evaluate
	 * @return A BigDecimal representing the fitness. Typically, 0 will be best 
	 * and higher numbers will represent less fit chromosomes
	 */
	public BigDecimal evaluate(Chromosome chromosome);
}
