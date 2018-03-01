-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema rubiconsensors02
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema rubiconsensors02
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `rubiconsensors02` DEFAULT CHARACTER SET utf8 ;
USE `rubiconsensors02` ;

-- -----------------------------------------------------
-- Table `rubiconsensors02`.`Payer`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rubiconsensors02`.`Payer` (
  `PayerID` INT NOT NULL,
  `UserName` VARCHAR(45) NULL,
  `Email` VARCHAR(90) NULL,
  `FirstName` VARCHAR(45) NULL,
  `LastName` VARCHAR(45) NULL,
  `Password` VARCHAR(100) NULL,
  `register_date` VARCHAR(100) NULL,
  PRIMARY KEY (`PayerID`),
  UNIQUE INDEX `PayerID_UNIQUE` (`PayerID` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rubiconsensors02`.`FlowSensor`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rubiconsensors02`.`FlowSensor` (
  `idFlowSensor` INT NOT NULL,
  `Payer_PayerID` INT NOT NULL,
  `Address` VARCHAR(100) NULL,
  PRIMARY KEY (`idFlowSensor`, `Payer_PayerID`),
  INDEX `fk_FlowSensor_Payer1_idx` (`Payer_PayerID` ASC),
  CONSTRAINT `fk_FlowSensor_Payer1`
    FOREIGN KEY (`Payer_PayerID`)
    REFERENCES `rubiconsensors02`.`Payer` (`PayerID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rubiconsensors02`.`Viewer`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rubiconsensors02`.`Viewer` (
  `idViewer` INT NOT NULL,
  `PayerID` INT NULL,
  `Login` VARCHAR(45) NULL,
  `FirstName` VARCHAR(45) NULL,
  `LastName` VARCHAR(45) NULL,
  `Email` VARCHAR(90) NULL,
  `Payer_PayerID` INT NOT NULL,
  PRIMARY KEY (`idViewer`, `Payer_PayerID`),
  INDEX `fk_Viewer_Payer1_idx` (`Payer_PayerID` ASC),
  CONSTRAINT `fk_Viewer_Payer1`
    FOREIGN KEY (`Payer_PayerID`)
    REFERENCES `rubiconsensors02`.`Payer` (`PayerID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rubiconsensors02`.`FlowSensorData`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rubiconsensors02`.`FlowSensorData` (
  `idFlowSensor` INT NOT NULL,
  `ISO8601` VARCHAR(100) NULL,
  `Data` INT(5) NULL,
  `FlowSensor_idFlowSensor` INT NOT NULL,
  PRIMARY KEY (`idFlowSensor`, `FlowSensor_idFlowSensor`),
  INDEX `fk_FlowSensorData_FlowSensor1_idx` (`FlowSensor_idFlowSensor` ASC),
  CONSTRAINT `fk_FlowSensorData_FlowSensor1`
    FOREIGN KEY (`FlowSensor_idFlowSensor`)
    REFERENCES `rubiconsensors02`.`FlowSensor` (`idFlowSensor`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rubiconsensors02`.`Viewer_has_FlowSensor`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rubiconsensors02`.`Viewer_has_FlowSensor` (
  `Viewer_idViewer` INT NOT NULL,
  `FlowSensor_idFlowSensor` INT NOT NULL,
  PRIMARY KEY (`Viewer_idViewer`, `FlowSensor_idFlowSensor`),
  INDEX `fk_Viewer_has_FlowSensor_FlowSensor1_idx` (`FlowSensor_idFlowSensor` ASC),
  INDEX `fk_Viewer_has_FlowSensor_Viewer_idx` (`Viewer_idViewer` ASC),
  CONSTRAINT `fk_Viewer_has_FlowSensor_Viewer`
    FOREIGN KEY (`Viewer_idViewer`)
    REFERENCES `rubiconsensors02`.`Viewer` (`idViewer`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Viewer_has_FlowSensor_FlowSensor1`
    FOREIGN KEY (`FlowSensor_idFlowSensor`)
    REFERENCES `rubiconsensors02`.`FlowSensor` (`idFlowSensor`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rubiconsensors02`.`User`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rubiconsensors02`.`User` (
  `idUser` INT NOT NULL,
  `Email` VARCHAR(45) NULL,
  `Name` VARCHAR(45) NULL,
  `FirstName` VARCHAR(45) NULL,
  `LastName` VARCHAR(45) NULL,
  `Address` VARCHAR(45) NULL,
  `Password` VARCHAR(45) NULL,
  `UserName` VARCHAR(45) NULL,
  `Usercol` VARCHAR(45) NULL,
  `Viewer_idViewer` INT NOT NULL,
  `Viewer_Payer_PayerID` INT NOT NULL,
  `Payer_PayerID` INT NOT NULL,
  PRIMARY KEY (`idUser`, `Viewer_idViewer`, `Viewer_Payer_PayerID`, `Payer_PayerID`),
  INDEX `fk_User_Viewer1_idx` (`Viewer_idViewer` ASC, `Viewer_Payer_PayerID` ASC),
  INDEX `fk_User_Payer1_idx` (`Payer_PayerID` ASC),
  CONSTRAINT `fk_User_Viewer1`
    FOREIGN KEY (`Viewer_idViewer` , `Viewer_Payer_PayerID`)
    REFERENCES `rubiconsensors02`.`Viewer` (`idViewer` , `Payer_PayerID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_User_Payer1`
    FOREIGN KEY (`Payer_PayerID`)
    REFERENCES `rubiconsensors02`.`Payer` (`PayerID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
